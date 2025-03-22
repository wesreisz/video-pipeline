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
        event: AWS Lambda event object (contains EventBridge event details or S3 event)
        context: AWS Lambda context object
    
    Returns:
        dict: Response containing success/failure information
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract records from either EventBridge or S3 event format
        records = []
        
        # Check for EventBridge format first (from Step Functions)
        if 'detail' in event:
            logger.info("Processing event from EventBridge/Step Functions")
            if 'requestParameters' in event['detail']:
                # Direct EventBridge S3 event
                records = [{
                    's3': {
                        'bucket': {'name': event['detail']['requestParameters']['bucketName']},
                        'object': {'key': event['detail']['requestParameters']['key']}
                    }
                }]
            else:
                # Passed through Step Functions
                records = event.get('detail', {}).get('records', [])
        
        # Fallback to direct S3 event format (for testing)
        if not records:
            records = event.get('Records', [])
        
        if not records:
            return {
                'statusCode': 400,
                'body': json.dumps('No records found in event')
            }
        
        # Extract bucket and key from record
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
        
        # Prepare response in EventBridge format
        output_bucket = os.environ.get('TRANSCRIPTION_OUTPUT_BUCKET')
        response = {
            'statusCode': 200,
            'detail': {
                'records': [{
                    's3': {
                        'bucket': {'name': output_bucket},
                        'object': {'key': output_key}
                    }
                }]
            },
            'body': json.dumps({
                'message': 'Transcription completed successfully',
                'bucket': bucket,
                'original_file': key,
                'transcription_file': output_key
            })
        }
        
        return response
    
    except Exception as e:
        return handle_error(e, "Error processing transcription request") 