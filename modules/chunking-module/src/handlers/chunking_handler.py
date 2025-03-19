import json
import logging
import os
# Change relative imports to absolute imports for Lambda compatibility
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_handler import handle_error
from services.chunking_service import ChunkingService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main entry point for the chunking Lambda function.
    
    Args:
        event: AWS Lambda event object (contains S3 event details or Step Functions input)
        context: AWS Lambda context object
    
    Returns:
        dict: Response containing success/failure information
    """
    try:
        logger.info("Hello World from Chunking Module!")
        
        # Check if event is None and raise an exception if it is
        if event is None:
            raise ValueError("Event cannot be None")
            
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle both direct S3 events and Step Functions invocations
        records = event.get('Records', [])
        
        # If no records found, check if this is from EventBridge/Step Functions
        if not records and 'detail' in event:
            logger.info("Processing event from Step Functions")
            # Extract records from detail object if available
            records = event.get('detail', {}).get('records', [])
        
        if records:
            s3_event = records[0].get('s3', {})
            source_bucket = s3_event.get('bucket', {}).get('name')
            source_key = s3_event.get('object', {}).get('key')
            
            if source_bucket and source_key:
                logger.info(f"Processing file {source_key} from bucket {source_bucket}")
                
                # Initialize service
                chunking_service = ChunkingService()
                
                # Process the transcription file
                output_key = chunking_service.process_media(source_bucket, source_key)
                
                # Get the output bucket from environment variable
                output_bucket = os.environ.get('CHUNKING_OUTPUT_BUCKET')
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Chunking completed successfully',
                        'source_bucket': source_bucket,
                        'source_file': source_key,
                        'output_bucket': output_bucket,
                        'output_key': output_key
                    })
                }
        
        # If not processing a file, just return success
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Chunking module initialized successfully',
                'event_received': event
            })
        }
    
    except Exception as e:
        logger.error(f"Error in chunking handler: {str(e)}")
        return handle_error(e, "Error in chunking module") 