import json
import logging
import os
from services.transcription_service import TranscriptionService
from utils.s3_utils import S3Utils
from utils.error_handler import handle_error

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main entry point for the transcription Lambda function.
    
    Args:
        event: AWS Lambda event object (contains S3 event details or Step Functions input)
        context: AWS Lambda context object
    
    Returns:
        dict: Response containing success/failure information
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle both direct S3 events and Step Functions invocations
        records = event.get('Records', [])
        
        # If no records found, check if this is from EventBridge/Step Functions
        if not records and 'detail' in event:
            logger.info("Processing event from EventBridge/Step Functions")
            # Extract records from detail object if available
            records = event.get('detail', {}).get('records', [])
        
        if not records:
            return {
                'statusCode': 400,
                'body': json.dumps('No records found in event')
            }
        
        # Extract bucket and key from S3 event
        s3_event = records[0].get('s3', {})
        bucket = s3_event.get('bucket', {}).get('name')
        key = s3_event.get('object', {}).get('key')
        
        if not bucket or not key:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing bucket or key information')
            }
            
        logger.info(f"Processing file {key} from bucket {bucket}")
        
        # Initialize services
        s3_utils = S3Utils()
        transcription_service = TranscriptionService()
        
        # Process the media file (audio or video)
        output_key = transcription_service.process_media(bucket, key)
        
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transcription completed successfully',
                'bucket': bucket,
                'original_file': key,
                'transcription_file': output_key
            })
        }
        
        # For Step Functions, include the output bucket and key in the response
        output_bucket = os.environ.get('TRANSCRIPTION_OUTPUT_BUCKET')
        if output_bucket:
            response['output_bucket'] = output_bucket
            response['output_key'] = output_key
            # Add formatted records for the next step
            response['detail'] = {
                'records': [
                    {
                        's3': {
                            'bucket': {
                                'name': output_bucket
                            },
                            'object': {
                                'key': output_key
                            }
                        }
                    }
                ]
            }
        
        return response
    
    except Exception as e:
        return handle_error(e, "Error processing transcription request") 