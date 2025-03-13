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
    input_bucket = 'test-audio-input'
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

def upload_test_file(bucket_name):
    """Upload a test audio file to the input bucket"""
    s3 = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Path to test audio file
    test_file = os.path.join(os.path.dirname(__file__), '..', '..', 'samples', 'sample.mp3')
    
    # Check if file exists
    if not os.path.exists(test_file):
        logger.error(f"Test file not found: {test_file}")
        # Create a dummy file for testing if the sample doesn't exist
        Path(test_file).parent.mkdir(parents=True, exist_ok=True)
        Path(test_file).write_bytes(b'dummy audio data')
        logger.info(f"Created dummy test file: {test_file}")
    
    # Upload to S3
    object_key = 'test_audio.mp3'
    s3.upload_file(test_file, bucket_name, object_key)
    logger.info(f"Uploaded test file to s3://{bucket_name}/{object_key}")
    
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
                return True
        
        logger.warning("No transcription results found in output bucket")
        return False
    
    except Exception as e:
        logger.error(f"Error checking transcription result: {str(e)}")
        return False

def main():
    """Run the local test"""
    logger.info("Starting local test for transcription Lambda")
    
    # Set up LocalStack environment
    input_bucket, output_bucket = setup_local_environment()
    
    # Upload test file
    object_key = upload_test_file(input_bucket)
    
    # Create simulated S3 event
    event = simulate_s3_event(input_bucket, object_key)
    
    # Modify the S3Utils class to use LocalStack endpoint for local testing
    # This is done through monkey patching to avoid changing the original code
    from utils.s3_utils import S3Utils
    original_init = S3Utils.__init__
    
    def patched_init(self):
        self.s3_client = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)
    
    # Apply the patch
    S3Utils.__init__ = patched_init
    
    try:
        # Execute the Lambda handler with the simulated event
        logger.info("Invoking Lambda handler with simulated S3 event")
        response = lambda_handler(event, {})
        
        logger.info(f"Lambda response: {json.dumps(response, indent=2)}")
        
        # Check for transcription result
        success = check_transcription_result(output_bucket, object_key)
        
        if success:
            logger.info("✅ Test completed successfully!")
        else:
            logger.error("❌ Test failed - no transcription result found")
            
    finally:
        # Restore the original implementation
        S3Utils.__init__ = original_init

if __name__ == "__main__":
    main() 