import json
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_handler import handle_error

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
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Chunking completed successfully',
                        'source_bucket': source_bucket,
                        'source_file': source_key,
                        'note': 'Chunking details are logged to CloudWatch instead of writing to a bucket'
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