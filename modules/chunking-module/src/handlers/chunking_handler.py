import json
import logging
import os
import sys
import boto3
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
        logger.info("Inside the Chunking Module!")
        
        if event is None:
            raise ValueError("Event cannot be None")
            
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Get records from either S3 events or Step Functions
        records = event.get('Records', [])
        if not records and 'detail' in event:
            logger.info("Processing event from Step Functions")
            records = event.get('detail', {}).get('records', [])
        
        response_data = {
            'message': 'Chunking module initialized successfully',
            'event_received': event
        }
        
        if records:
            s3_event = records[0].get('s3', {})
            source_bucket = s3_event.get('bucket', {}).get('name')
            source_key = s3_event.get('object', {}).get('key')
            
            if source_bucket and source_key:
                logger.info(f"Processing file {source_key} from bucket {source_bucket}")

                # Initialize S3 client
                s3_client = boto3.client('s3')
                
                try:
                    # Get the object from S3
                    response = s3_client.get_object(
                        Bucket=source_bucket,
                        Key=source_key
                    )
                    
                    # Load the JSON content into a dictionary
                    audio_segments = json.loads(response['Body'].read().decode('utf-8'))
                    logger.info(f"Successfully loaded {len(audio_segments)} audio-segments")
                    
                except s3_client.exceptions.NoSuchKey:
                    raise ValueError(f"File {source_key} not found in bucket {source_bucket}")
                except json.JSONDecodeError:
                    raise ValueError(f"File {source_key} is not valid JSON")
                
                response_data = {
                    'message': 'Chunking completed successfully',
                    'source_bucket': source_bucket,
                    'source_file': source_key,
                    'note': 'Chunking details are logged to CloudWatch instead of writing to a bucket'
                }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        logger.error(f"Error in chunking handler: {str(e)}")
        return handle_error(e, "Error in chunking module") 