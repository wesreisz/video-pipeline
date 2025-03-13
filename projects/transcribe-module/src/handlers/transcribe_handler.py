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
        event: AWS Lambda event object (contains S3 event details)
        context: AWS Lambda context object
    
    Returns:
        dict: Response containing success/failure information
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract bucket and key from S3 event
        records = event.get('Records', [])
        if not records:
            return {
                'statusCode': 400,
                'body': json.dumps('No records found in event')
            }
        
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
        
        # Process the audio file
        output_key = transcription_service.process_audio(bucket, key)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transcription completed successfully',
                'bucket': bucket,
                'original_file': key,
                'transcription_file': output_key
            })
        }
    
    except Exception as e:
        return handle_error(e, "Error processing transcription request") 