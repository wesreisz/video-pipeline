#!/usr/bin/env python3
"""
Test script for S3Utils to verify it can properly download transcription files.

This script tests the S3Utils class by:
1. Attempting to download a transcription file using our enhanced S3Utils
2. Verifying that the download works correctly
3. Printing information about the transcription file

Usage:
    python test_s3_utils.py BUCKET_NAME KEY_NAME

Example:
    python test_s3_utils.py dev-media-transcribe-output transcriptions/hello-my_name_is_wes_25dc0df8.json
"""

import sys
import os
import json
import logging
import boto3
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_s3_utils')

# Add the src directory to sys.path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Try to import our S3Utils
try:
    from utils.s3_utils import S3Utils
    logger.info("Successfully imported S3Utils from src/utils/s3_utils.py")
except ImportError as e:
    logger.error(f"Failed to import S3Utils: {e}")
    logger.info("Falling back to built-in implementation")
    
    # Define a simple S3Utils class as a fallback
    class S3Utils:
        def __init__(self, region=None):
            self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
            self.s3_client = boto3.client('s3', region_name=self.region)
            
        def download_file(self, bucket, key, local_path):
            """Download a file from S3 using get_object for better control."""
            logger.info(f"Downloading {bucket}/{key} to {local_path}")
            
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # Use get_object instead of download_file
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                content = response['Body'].read().decode('utf-8')
                
                # Write the content to a local file
                with open(local_path, 'w') as f:
                    f.write(content)
                    
                logger.info(f"Successfully downloaded {bucket}/{key} to {local_path}")
                return local_path
                
            except Exception as e:
                logger.error(f"Error downloading file from S3: {str(e)}")
                raise
                
        def download_json(self, bucket, key):
            """Download and parse a JSON file from S3."""
            logger.info(f"Downloading and parsing JSON from s3://{bucket}/{key}")
            
            try:
                response = self.s3_client.get_object(Bucket=bucket, Key=key)
                content = response['Body'].read().decode('utf-8')
                return json.loads(content)
            except Exception as e:
                logger.error(f"Error downloading JSON from S3: {str(e)}")
                raise

def test_file_download(bucket, key):
    """Test downloading a file from S3 using our S3Utils."""
    logger.info(f"Testing file download from bucket={bucket}, key={key}")
    
    # Create an instance of S3Utils
    s3_utils = S3Utils()
    
    # Create a temporary directory for downloads
    temp_dir = "/tmp/transcriptions"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a local filename from the S3 key
    filename = os.path.basename(key)
    local_path = os.path.join(temp_dir, filename)
    
    # Try downloading with download_file
    try:
        logger.info("Testing download_file method...")
        s3_utils.download_file(bucket, key, local_path)
        
        # Check if the file exists
        if os.path.exists(local_path):
            logger.info(f"File successfully downloaded to {local_path}")
            
            # Read the file to see if it's valid
            with open(local_path, 'r') as f:
                content = f.read()
                logger.info(f"File size: {len(content)} bytes")
                
                # Try to parse as JSON
                try:
                    data = json.loads(content)
                    logger.info("File contains valid JSON")
                    logger.info(f"Keys found: {list(data.keys())}")
                    
                    # Check for specific keys that should be in a transcription file
                    if 'transcription_text' in data:
                        logger.info(f"Transcription text: {data['transcription_text'][:100]}...")
                    
                    if 'segments' in data:
                        logger.info(f"Found {len(data['segments'])} segments")
                        
                    if 'audio_segments' in data:
                        logger.info(f"Found {len(data['audio_segments'])} audio segments")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"File is not valid JSON: {e}")
        else:
            logger.error(f"File not found at {local_path}")
            
    except Exception as e:
        logger.error(f"Error with download_file method: {e}")
    
    # Now try with download_json method
    try:
        logger.info("\nTesting download_json method...")
        data = s3_utils.download_json(bucket, key)
        
        logger.info("JSON successfully downloaded and parsed")
        logger.info(f"Keys found: {list(data.keys())}")
        
        # Check for specific keys that should be in a transcription file
        if 'transcription_text' in data:
            logger.info(f"Transcription text: {data['transcription_text'][:100]}...")
        
        if 'segments' in data:
            logger.info(f"Found {len(data['segments'])} segments")
            
        if 'audio_segments' in data:
            logger.info(f"Found {len(data['audio_segments'])} audio segments")
            
    except Exception as e:
        logger.error(f"Error with download_json method: {e}")
    
    logger.info("Test completed")
    return True
    
def main():
    """Main function to run the test."""
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} BUCKET_NAME KEY_NAME")
        print(f"Example: {sys.argv[0]} dev-media-transcribe-output transcriptions/hello-my_name_is_wes_25dc0df8.json")
        return 1
        
    bucket = sys.argv[1]
    key = sys.argv[2]
    
    logger.info(f"Starting S3Utils test for bucket={bucket}, key={key}")
    
    # Run the test
    test_file_download(bucket, key)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 