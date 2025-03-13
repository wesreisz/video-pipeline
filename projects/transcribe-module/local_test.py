#!/usr/bin/env python3
import json
import os
import sys
import boto3
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the Lambda handler
from handlers.transcribe_handler import lambda_handler

# LocalStack endpoint
LOCALSTACK_ENDPOINT = 'http://localhost:4566'

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

def upload_test_file(bucket_name, file_type='audio'):
    """Upload a test media file to the input bucket
    
    Args:
        bucket_name (str): S3 bucket name
        file_type (str): Type of file to upload ('audio' or 'video')
        
    Returns:
        str: The S3 object key for the uploaded file
    """
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Path to test file based on type
    if file_type == 'audio':
        filename = 'sample.mp3'
        folder = 'audio'
        object_key = f'{folder}/test_audio.mp3'
    else:  # video
        filename = 'sample.mp4'
        folder = 'videos'
        object_key = f'{folder}/test_video.mp4'
    
    test_file = os.path.join(os.path.dirname(__file__), '..', '..', 'samples', filename)
    
    # Check if file exists
    if not os.path.exists(test_file):
        logger.warning(f"Test file not found: {test_file}")
        # Create a dummy file for testing if the sample doesn't exist
        Path(test_file).parent.mkdir(parents=True, exist_ok=True)
        Path(test_file).write_bytes(b'dummy media data')
        logger.info(f"Created dummy test file: {test_file}")
    
    # Upload to S3
    s3.upload_file(test_file, bucket_name, object_key)
    logger.info(f"Uploaded test {file_type} file to s3://{bucket_name}/{object_key}")
    
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

def check_transcription_result(output_bucket, expected_key):
    """Check if the transcription result was created in the output bucket"""
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Give Lambda some time to process
    logger.info("Waiting for transcription to complete...")
    time.sleep(2)
    
    try:
        # List objects in the output bucket
        response = s3.list_objects_v2(Bucket=output_bucket, Prefix='transcriptions/')
        
        if 'Contents' in response:
            for obj in response['Contents']:
                logger.info(f"Found output file: {obj['Key']}")
                
                # Get the content of the first file
                result = s3.get_object(Bucket=output_bucket, Key=obj['Key'])
                content = json.loads(result['Body'].read().decode('utf-8'))
                logger.info(f"Transcription content: {json.dumps(content, indent=2)}")
                
                # Verify the media_type field
                if 'media_type' in content:
                    logger.info(f"Media type in result: {content['media_type']}")
                
                return True
        
        logger.warning("No transcription results found in output bucket")
        return False
    
    except Exception as e:
        logger.error(f"Error checking transcription result: {str(e)}")
        return False

def test_media_transcription(input_bucket, output_bucket, media_type):
    """Test transcription for a specific media type"""
    logger.info(f"Testing {media_type} transcription")
    
    # Upload test file
    object_key = upload_test_file(input_bucket, media_type)
    
    # Create simulated S3 event
    event = simulate_s3_event(input_bucket, object_key)
    
    # Execute the Lambda handler with the simulated event
    logger.info(f"Invoking Lambda handler with simulated S3 event for {media_type}")
    response = lambda_handler(event, {})
    
    logger.info(f"Lambda response: {json.dumps(response, indent=2)}")
    
    # Check for transcription result
    success = check_transcription_result(output_bucket, object_key)
    
    if success:
        logger.info(f"✅ {media_type.capitalize()} transcription test completed successfully!")
    else:
        logger.error(f"❌ {media_type.capitalize()} transcription test failed - no result found")
    
    return success

def main():
    """Run the local test"""
    logger.info("Starting local test for media transcription Lambda")
    
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
    
    try:
        # Test both audio and video transcription
        audio_success = test_media_transcription(input_bucket, output_bucket, 'audio')
        video_success = test_media_transcription(input_bucket, output_bucket, 'video')
        
        if audio_success and video_success:
            logger.info("✅ All tests completed successfully!")
        else:
            logger.error("❌ One or more tests failed")
            
    finally:
        # Restore the original implementation
        S3Utils.__init__ = original_init

if __name__ == "__main__":
    main() 