#!/usr/bin/env python3
import json
import os
import sys
import boto3
import time
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the Lambda handler
from handlers.transcribe_handler import lambda_handler
from services.transcription_service import TranscriptionService
from models.transcription_result import TranscriptionResult

# LocalStack endpoint
LOCALSTACK_ENDPOINT = 'http://localhost:4566'
# Specific video file to test
VIDEO_FILE_PATH = '/Users/wesleyreisz/work/qcon/video-pipeline/samples/AYAWA-Spring-QConPlus-Spring-2021.mp4'

def setup_local_environment():
    """Set up the local test environment with LocalStack"""
    # Create S3 client pointing to LocalStack
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Create test buckets
    input_bucket = 'test-media-input'
    output_bucket = 'test-transcription-output'
    
    try:
        s3.create_bucket(Bucket=input_bucket)
        logger.info(f"Created input bucket: {input_bucket}")
        
        s3.create_bucket(Bucket=output_bucket)
        logger.info(f"Created output bucket: {output_bucket}")
    except Exception as e:
        # Buckets might already exist
        logger.warning(f"Error creating buckets (they may already exist): {str(e)}")
    
    # Set environment variable for the Lambda function
    os.environ['TRANSCRIPTION_OUTPUT_BUCKET'] = output_bucket
    
    return input_bucket, output_bucket

def upload_test_video(bucket_name):
    """Upload the specified video file to the input bucket
    
    Args:
        bucket_name (str): S3 bucket name
        
    Returns:
        str: The S3 object key for the uploaded file
    """
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Check if file exists
    if not os.path.exists(VIDEO_FILE_PATH):
        logger.error(f"Test video file not found: {VIDEO_FILE_PATH}")
        raise FileNotFoundError(f"Video file not found: {VIDEO_FILE_PATH}")
    
    # Upload to S3
    filename = os.path.basename(VIDEO_FILE_PATH)
    object_key = f'videos/{filename}'
    s3.upload_file(VIDEO_FILE_PATH, bucket_name, object_key)
    logger.info(f"Uploaded test video file to s3://{bucket_name}/{object_key}")
    
    return object_key

def simulate_s3_event(bucket_name, object_key):
    """Create a simulated S3 event"""
    return {
        'Records': [{
            's3': {
                'bucket': {'name': bucket_name},
                'object': {'key': object_key}
            }
        }]
    }

def mock_transcribe_service():
    """Mock the AWS Transcribe service for local testing"""
    # Create a mock for TranscriptionService._wait_for_transcription
    original_wait = TranscriptionService._wait_for_transcription
    
    def mock_wait_for_transcription(self, job_name, max_attempts=30, delay_seconds=10):
        logger.info(f"Using mocked transcription service. Would have waited for job: {job_name}")
        logger.info("Returning mock transcription result")
        return "This is a mock transcription for the AYAWA Spring QCon Plus video. The mock transcription service has processed this video file successfully."
    
    # Apply the patch
    TranscriptionService._wait_for_transcription = mock_wait_for_transcription
    
    # Also mock the start_transcription_job method of boto3 client
    original_client = boto3.client
    
    def mock_client(*args, **kwargs):
        if args and args[0] == 'transcribe':
            mock = MagicMock()
            mock.start_transcription_job = MagicMock(return_value={"TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}})
            mock.get_transcription_job = MagicMock(return_value={"TranscriptionJob": {"TranscriptionJobStatus": "COMPLETED"}})
            return mock
        else:
            return original_client(*args, **kwargs)
    
    boto3.client = mock_client
    
    return {
        'restore_wait': lambda: setattr(TranscriptionService, '_wait_for_transcription', original_wait),
        'restore_client': lambda: setattr(boto3, 'client', original_client)
    }

def check_transcription_result(output_bucket, object_key):
    """Check if the transcription result was created in the output bucket"""
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Give Lambda some time to process
    logger.info("Waiting for transcription to complete...")
    
    try:
        # List objects in the output bucket
        response = s3.list_objects_v2(Bucket=output_bucket, Prefix='transcriptions/')
        
        if 'Contents' in response:
            logger.info(f"Found {len(response['Contents'])} files in transcriptions/")
            for obj in response['Contents']:
                logger.info(f"Checking file: {obj['Key']}")
                # Get the filename from the original video path
                video_filename = os.path.basename(VIDEO_FILE_PATH)
                # Get the filename from the output key
                output_filename = os.path.basename(obj['Key'])
                
                # Strip extensions for comparison
                video_name = os.path.splitext(video_filename)[0]
                output_name = os.path.splitext(output_filename)[0]
                
                logger.info(f"Comparing: '{video_name}' with '{output_name}'")
                # Do a case-insensitive comparison
                if video_name.lower() == output_name.lower():
                    logger.info(f"Found matching output file: {obj['Key']}")
                    
                    # Get the content of the file
                    result = s3.get_object(Bucket=output_bucket, Key=obj['Key'])
                    content = json.loads(result['Body'].read().decode('utf-8'))
                    logger.info(f"Transcription content: {json.dumps(content, indent=2)}")
                    
                    # Verify the media_type field
                    if 'media_type' in content:
                        logger.info(f"Media type in result: {content['media_type']}")
                        if content['media_type'] == 'video':
                            logger.info("✅ Confirmed media_type is correctly set to 'video'")
                    
                    return True
        
        logger.warning("No matching transcription results found in output bucket")
        return False
        
    except Exception as e:
        logger.error(f"Error checking transcription result: {str(e)}")
        return False

def main():
    """Run the video transcription test"""
    logger.info("Starting video transcription test for specific video")
    logger.info(f"Testing file: {VIDEO_FILE_PATH}")
    
    # Set up LocalStack environment
    input_bucket, output_bucket = setup_local_environment()
    
    # Modify the S3Utils class to use LocalStack endpoint for local testing
    # This is done through monkey patching to avoid changing the original code
    from utils.s3_utils import S3Utils
    original_init = S3Utils.__init__
    
    def patched_init(self):
        self.s3_client = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Apply the patch
    S3Utils.__init__ = patched_init
    
    # Mock the AWS Transcribe service
    mock_restorers = mock_transcribe_service()
    
    try:
        # Upload the video file
        object_key = upload_test_video(input_bucket)
        
        # Create simulated S3 event
        event = simulate_s3_event(input_bucket, object_key)
        
        # Execute the Lambda handler with the simulated event
        logger.info("Invoking Lambda handler with simulated S3 event for video file")
        response = lambda_handler(event, {})
        
        logger.info(f"Lambda response: {json.dumps(response, indent=2)}")
        
        # Check for transcription result
        success = check_transcription_result(output_bucket, object_key)
        
        if success:
            logger.info("✅ Video transcription test completed successfully!")
        else:
            logger.error("❌ Video transcription test failed - no transcription result found")
            
    finally:
        # Restore the original implementations
        S3Utils.__init__ = original_init
        mock_restorers['restore_wait']()
        mock_restorers['restore_client']()

if __name__ == "__main__":
    main() 