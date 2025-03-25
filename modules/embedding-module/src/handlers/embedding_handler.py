import json
import logging
import os
from typing import Dict, Any, List

from services.openai_service import OpenAIService, OpenAIServiceError
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Initialize OpenAI service lazily
_openai_service = None

def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing SQS messages and creating embeddings.
    
    Args:
        event: AWS Lambda event containing SQS messages
        context: AWS Lambda context
        
    Returns:
        Dict containing the processing status and results
    """
    try:
        logger.info("Starting embedding process")
        logger.debug("Received event: %s", json.dumps(event))
        
        # Get OpenAI service
        openai_service = get_openai_service()
        
        # Process each record in the SQS batch
        processed_records = []
        for record in event.get('Records', []):
            try:
                # Parse SQS message
                message_body = json.loads(record['body'])
                chunk_id = message_body.get('chunk_id', f"chunk_{message_body.get('start_time', 0)}_{message_body.get('end_time', 0)}")
                text_content = message_body.get('text', '')
                
                # Log chunk processing with exact format
                logger.info("Processing chunk %s: %s", chunk_id, text_content)
                
                # Create embedding using OpenAI service
                embedding_response = openai_service.create_embedding(text_content)
                
                # Add to processed records with embedding data
                processed_records.append({
                    'chunk_id': chunk_id,
                    'status': 'success',
                    'text_length': len(text_content),
                    'embedding': embedding_response.embedding,
                    'model': embedding_response.model,
                    'usage': embedding_response.usage
                })
                
            except OpenAIServiceError as e:
                logger.error("OpenAI service error processing record: %s", str(e), exc_info=True)
                processed_records.append({
                    'chunk_id': 'unknown',
                    'status': 'error',
                    'error': f"OpenAI service error: {str(e)}"
                })
            except json.JSONDecodeError as e:
                logger.error("Error decoding JSON: %s", str(e), exc_info=True)
                processed_records.append({
                    'chunk_id': 'unknown',
                    'status': 'error',
                    'error': f"Invalid JSON format: {str(e)}"
                })
            except Exception as e:
                logger.error("Error processing record: %s", str(e), exc_info=True)
                processed_records.append({
                    'chunk_id': 'unknown',
                    'status': 'error',
                    'error': str(e)
                })
        
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