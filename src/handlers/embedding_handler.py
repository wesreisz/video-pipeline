import json
import logging
import os
from typing import Dict, Any, List

from ..services.openai_service import OpenAIService
from ..services.pinecone_service import PineconeService
from ..utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

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
        
        # Initialize services
        openai_service = OpenAIService()
        pinecone_service = PineconeService()
        
        # Process each record in the SQS batch
        processed_records = []
        for record in event.get('Records', []):
            try:
                # Parse SQS message
                message_body = json.loads(record['body'])
                logger.info("Processing message: %s", message_body)
                
                # Extract text content from message
                text_content = message_body.get('text', '')
                chunk_id = message_body.get('chunk_id', '')
                
                if not text_content or not chunk_id:
                    logger.error("Missing required fields in message: %s", message_body)
                    processed_records.append({
                        'chunk_id': chunk_id or 'unknown',
                        'status': 'error',
                        'error': 'Missing required fields: text or chunk_id'
                    })
                    continue
                
                # Generate embeddings using OpenAI
                embeddings = openai_service.create_embedding(text_content)
                
                # Store embeddings in Pinecone
                pinecone_service.upsert_embeddings(chunk_id, embeddings, {'text': text_content})
                
                processed_records.append({
                    'chunk_id': chunk_id,
                    'status': 'success'
                })
                
                logger.info("Successfully processed chunk: %s", chunk_id)
                
            except Exception as e:
                logger.error("Error processing record: %s", str(e), exc_info=True)
                processed_records.append({
                    'chunk_id': message_body.get('chunk_id', 'unknown'),
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