import json
import logging
import os
from typing import Dict, Any, List

from services.openai_service import OpenAIService, OpenAIServiceError
from services.pinecone_service import PineconeService, PineconeServiceError, TalkMetadata
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize services lazily
_openai_service = None
_pinecone_service = None

def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

def get_pinecone_service() -> PineconeService:
    """Get or create Pinecone service instance."""
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service

def parse_metadata(message_body: Dict) -> TalkMetadata:
    """
    Parse metadata from message body, using empty/default values for any missing fields.
    If metadata size exceeds Pinecone's limit, it will be logged as a warning and the metadata
    will be returned without the text field to reduce size.
    
    Args:
        message_body: Dict containing the SQS message body
        
    Returns:
        TalkMetadata object with available fields populated
    """
    metadata_obj = message_body.get('metadata', {})
    
    metadata = TalkMetadata(
        speaker=metadata_obj.get('speaker', []),
        start_time=message_body.get('start_time', '0.0'),
        end_time=message_body.get('end_time', '0.0'),
        title=metadata_obj.get('title', ''),
        track=metadata_obj.get('track', ''),
        day=metadata_obj.get('day', ''),
        text=message_body.get('text', ''),
        original_file=message_body.get('original_file', ''),
        segment_id=message_body.get('segment_id', '')
    )
    
    metadata_dict = {
        "speaker": metadata.speaker,
        "start_time": metadata.start_time,
        "end_time": metadata.end_time,
        "title": metadata.title,
        "track": metadata.track,
        "day": metadata.day,
        "text": metadata.text,
        "original_file": metadata.original_file,
        "segment_id": metadata.segment_id
    }
    
    metadata_size = len(json.dumps(metadata_dict).encode('utf-8'))
    max_size = 40 * 1024  # 40KB in bytes
    
    if metadata_size > max_size:
        logger.warning(
            "Metadata size (%d bytes) exceeds Pinecone's 40KB limit. Removing text field from metadata.",
            metadata_size
        )
        # Create new metadata without the text field to reduce size
        metadata = TalkMetadata(
            speaker=metadata_obj.get('speaker', []),
            start_time=message_body.get('start_time', '0.0'),
            end_time=message_body.get('end_time', '0.0'),
            title=metadata_obj.get('title', ''),
            track=metadata_obj.get('track', ''),
            day=metadata_obj.get('day', ''),
            text='',  # Remove text to reduce size
            original_file=message_body.get('original_file', ''),
            segment_id=message_body.get('segment_id', '')
        )
        
        # Verify new size
        metadata_dict = {
            "speaker": metadata.speaker,
            "start_time": metadata.start_time,
            "end_time": metadata.end_time,
            "title": metadata.title,
            "track": metadata.track,
            "day": metadata.day,
            "text": metadata.text,
            "original_file": metadata.original_file,
            "segment_id": metadata.segment_id
        }
        new_size = len(json.dumps(metadata_dict).encode('utf-8'))
        logger.info("Reduced metadata size to %d bytes", new_size)
    
    return metadata

def create_error_record(chunk_id: str = 'unknown', error: Exception = None) -> Dict:
    """Helper function to create consistent error records"""
    return {
        'chunk_id': chunk_id,
        'status': 'error',
        'error': str(error)
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing SQS messages, creating embeddings,
    and storing them in Pinecone.
    """
    try:
        logger.info("Starting embedding process with event: %s", json.dumps(event))
        
        openai_service = get_openai_service()
        pinecone_service = get_pinecone_service()
        
        processed_records = []
        for record in event.get('Records', []):
            try:
                message_body = json.loads(record['body'])
                chunk_id = message_body.get('chunk_id', 'unknown_chunk')
                text_content = message_body.get('text', '')
                
                metadata = parse_metadata(message_body)
                logger.info("Processing chunk %s - Metadata: %s", chunk_id, metadata)
                
                embedding_response = openai_service.create_embedding(text_content)
                
                upsert_response = pinecone_service.upsert_embeddings(
                    vectors=[embedding_response.embedding],
                    ids=[chunk_id],
                    metadata=[metadata]
                )
                
                processed_records.append({
                    'chunk_id': chunk_id,
                    'status': 'success',
                    'text_length': len(text_content),
                    'embedding': embedding_response.embedding,
                    'model': embedding_response.model,
                    'usage': embedding_response.usage,
                    'storage_status': {
                        'upserted_count': upsert_response.upserted_count,
                        'namespace': upsert_response.namespace
                    }
                })
                
            except (OpenAIServiceError, PineconeServiceError, json.JSONDecodeError) as e:
                logger.error("Error processing record: %s", str(e), exc_info=True)
                processed_records.append(create_error_record(
                    chunk_id if 'chunk_id' in locals() else 'unknown',
                    e
                ))
            except Exception as e:
                logger.error("Unexpected error processing record: %s", str(e), exc_info=True)
                processed_records.append(create_error_record(
                    chunk_id if 'chunk_id' in locals() else 'unknown',
                    e
                ))
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Embedding process completed',
                'processed_records': processed_records
            })
        }
        
    except Exception as e:
        logger.error("Fatal error in lambda handler: %s", str(e), exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing embeddings',
                'error': str(e)
            })
        } 