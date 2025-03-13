#!/usr/bin/env python3
"""
End-to-End Test for AWS Transcribe Module

This script automates the end-to-end testing of the AWS Transcribe module,
performing all steps from creating a test audio file to verifying transcription output.
"""

import os
import sys
import time
import json
import logging
import argparse
import boto3
import subprocess
import requests
from botocore.exceptions import ClientError
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"transcribe_e2e_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

class TranscribeE2ETest:
    """Class to run end-to-end tests for the AWS Transcribe module"""
    
    def __init__(self, input_bucket, output_bucket, region='us-east-1', lambda_name='dev_audio_transcribe'):
        """
        Initialize the test with configuration parameters
        
        Args:
            input_bucket (str): S3 bucket for input audio files
            output_bucket (str): S3 bucket for transcription output
            region (str): AWS region to use
            lambda_name (str): Name of the Lambda function
        """
        self.input_bucket = input_bucket
        self.output_bucket = output_bucket
        self.region = region
        self.lambda_name = lambda_name
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_file = os.path.join(self.test_dir, 'speech-sample.mp3')
        
        # AWS clients
        self.s3_client = boto3.client('s3', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        self.polly_client = boto3.client('polly', region_name=region)
        
        # Expected text for verification
        self.expected_text = "This is a test of the audio transcription service. We are testing the end to end workflow from audio creation to transcription output."
        
    def create_test_audio(self):
        """
        Create a test audio file with speech content using either a download or AWS Polly
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Creating test audio file...")
        
        # First attempt: Download a sample audio file
        try:
            logger.info("Attempting to download sample audio file...")
            sample_url = "https://filesamples.com/samples/audio/mp3/sample3.mp3"
            response = requests.get(sample_url)
            if response.status_code == 200:
                with open(self.audio_file, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded sample audio to {self.audio_file}")
                return True
        except Exception as e:
            logger.warning(f"Failed to download sample audio: {str(e)}")
        
        # Second attempt: Use AWS Polly to create speech
        try:
            logger.info("Creating audio file using AWS Polly...")
            response = self.polly_client.synthesize_speech(
                Text=self.expected_text,
                OutputFormat="mp3",
                VoiceId="Joanna"
            )
            
            if "AudioStream" in response:
                with open(self.audio_file, 'wb') as f:
                    f.write(response['AudioStream'].read())
                logger.info(f"Created audio file using AWS Polly: {self.audio_file}")
                return True
        except Exception as e:
            logger.error(f"Failed to create audio with AWS Polly: {str(e)}")
        
        logger.error("Failed to create test audio file using both methods")
        return False
    
    def verify_audio_file(self):
        """
        Verify the audio file exists and has appropriate content
        
        Returns:
            bool: True if verified, False otherwise
        """
        if not os.path.exists(self.audio_file):
            logger.error(f"Audio file {self.audio_file} does not exist")
            return False
        
        file_size = os.path.getsize(self.audio_file)
        logger.info(f"Audio file verified: {self.audio_file} ({file_size} bytes)")
        
        if file_size < 1000:  # Arbitrary minimum size check
            logger.warning(f"Audio file is suspiciously small: {file_size} bytes")
        
        return True
    
    def upload_to_input_bucket(self):
        """
        Upload the audio file to the input S3 bucket
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Uploading audio file to s3://{self.input_bucket}/speech-sample.mp3")
        try:
            self.s3_client.upload_file(
                self.audio_file, 
                self.input_bucket, 
                os.path.basename(self.audio_file)
            )
            logger.info("Upload successful")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return False
    
    def get_latest_log_stream(self):
        """
        Get the most recent log stream for the Lambda function
        
        Returns:
            str: Log stream name or None if not found
        """
        log_group_name = f"/aws/lambda/{self.lambda_name}"
        try:
            response = self.logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=1
            )
            
            if not response.get('logStreams'):
                logger.warning("No log streams found")
                return None
                
            return response['logStreams'][0]['logStreamName']
        except Exception as e:
            logger.error(f"Error getting log streams: {str(e)}")
            return None
    
    def monitor_processing(self, max_wait=60, check_interval=5):
        """
        Monitor the Lambda function's processing by checking CloudWatch logs
        
        Args:
            max_wait (int): Maximum time to wait in seconds
            check_interval (int): Interval between checks in seconds
            
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        logger.info(f"Monitoring Lambda processing (timeout: {max_wait}s)...")
        log_group_name = f"/aws/lambda/{self.lambda_name}"
        
        start_time = time.time()
        while (time.time() - start_time) < max_wait:
            log_stream = self.get_latest_log_stream()
            if not log_stream:
                time.sleep(check_interval)
                continue
                
            try:
                response = self.logs_client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName=log_stream,
                    limit=20
                )
                
                for event in response.get('events', []):
                    message = event.get('message', '')
                    
                    # Log important messages
                    if "ERROR" in message or "error" in message.lower():
                        logger.error(f"Lambda error: {message}")
                    elif "Transcription job" in message and "completed successfully" in message:
                        logger.info("Transcription job completed successfully")
                        return True
                    elif "Transcription complete" in message:
                        logger.info("Transcription process completed")
                        return True
            
            except Exception as e:
                logger.error(f"Error monitoring logs: {str(e)}")
            
            elapsed = time.time() - start_time
            logger.info(f"Waiting for processing to complete ({int(elapsed)}s / {max_wait}s)...")
            time.sleep(check_interval)
        
        logger.warning(f"Monitoring timed out after {max_wait} seconds")
        return False
    
    def verify_transcription_output(self, wait_time=10):
        """
        Verify transcription output in the S3 bucket
        
        Args:
            wait_time (int): Additional wait time in seconds
            
        Returns:
            bool: True if verified, False otherwise
        """
        # Additional wait time for AWS S3 consistency
        logger.info(f"Waiting {wait_time}s for S3 consistency...")
        time.sleep(wait_time)
        
        logger.info("Verifying transcription output...")
        output_key = f"transcriptions/{os.path.splitext(os.path.basename(self.audio_file))[0]}.json"
        
        try:
            # Check if the output file exists
            objects = self.s3_client.list_objects_v2(
                Bucket=self.output_bucket,
                Prefix="transcriptions/"
            )
            
            if 'Contents' not in objects:
                logger.error("No objects found in transcriptions/ prefix")
                return False
                
            found = False
            for obj in objects['Contents']:
                if obj['Key'] == output_key:
                    found = True
                    break
                    
            if not found:
                logger.error(f"Transcription file not found at s3://{self.output_bucket}/{output_key}")
                logger.info("Available files:")
                for obj in objects['Contents']:
                    logger.info(f"  - {obj['Key']}")
                return False
                
            # Get the transcription content
            response = self.s3_client.get_object(
                Bucket=self.output_bucket,
                Key=output_key
            )
            
            content = response['Body'].read().decode('utf-8')
            result = json.loads(content)
            
            # Log the result
            logger.info(f"Transcription result: {json.dumps(result, indent=2)}")
            
            # Verify the structure
            required_fields = ['original_file', 'transcription_text', 'timestamp', 'job_name']
            for field in required_fields:
                if field not in result:
                    logger.error(f"Transcription output missing required field: {field}")
                    return False
            
            logger.info("Transcription output verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying transcription output: {str(e)}")
            return False
    
    def clean_up(self):
        """
        Clean up test resources
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Cleaning up test resources...")
        success = True
        
        # Remove from input bucket
        try:
            logger.info(f"Removing audio file from S3 input bucket...")
            self.s3_client.delete_object(
                Bucket=self.input_bucket,
                Key=os.path.basename(self.audio_file)
            )
        except Exception as e:
            logger.error(f"Failed to clean up input file: {str(e)}")
            success = False
        
        # Remove from output bucket
        try:
            logger.info(f"Removing transcription from S3 output bucket...")
            output_key = f"transcriptions/{os.path.splitext(os.path.basename(self.audio_file))[0]}.json"
            self.s3_client.delete_object(
                Bucket=self.output_bucket,
                Key=output_key
            )
        except Exception as e:
            logger.error(f"Failed to clean up output file: {str(e)}")
            success = False
        
        # Remove local file
        try:
            if os.path.exists(self.audio_file):
                logger.info(f"Removing local audio file...")
                os.remove(self.audio_file)
        except Exception as e:
            logger.error(f"Failed to remove local file: {str(e)}")
            success = False
        
        return success
    
    def run_test(self):
        """
        Run the complete end-to-end test
        
        Returns:
            bool: True if the test passed, False otherwise
        """
        logger.info("="*80)
        logger.info("STARTING END-TO-END TEST OF AWS TRANSCRIBE MODULE")
        logger.info("="*80)
        
        try:
            # Step 1: Create audio file
            if not self.create_test_audio():
                logger.error("Test failed at step 1: Create audio file")
                return False
                
            # Step 2: Verify audio file
            if not self.verify_audio_file():
                logger.error("Test failed at step 2: Verify audio file")
                return False
                
            # Step 3: Upload to input bucket
            if not self.upload_to_input_bucket():
                logger.error("Test failed at step 3: Upload to input bucket")
                return False
                
            # Step 4: Monitor processing
            if not self.monitor_processing(max_wait=120):  # 2 minutes timeout
                logger.warning("Monitoring timed out, but continuing with verification")
                
            # Step 5: Verify transcription output
            if not self.verify_transcription_output(wait_time=15):
                logger.error("Test failed at step 5: Verify transcription output")
                self.clean_up()
                return False
                
            # Step 6: Clean up
            self.clean_up()
            
            logger.info("="*80)
            logger.info("END-TO-END TEST COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            return True
            
        except Exception as e:
            logger.error(f"Test failed with unexpected error: {str(e)}")
            self.clean_up()
            return False


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='End-to-end test for AWS Transcribe module')
    
    parser.add_argument('--input-bucket', default='dev-audio-transcribe-input',
                        help='S3 bucket for input audio files')
    parser.add_argument('--output-bucket', default='dev-audio-transcribe-output',
                        help='S3 bucket for transcription output')
    parser.add_argument('--region', default='us-east-1',
                        help='AWS region to use')
    parser.add_argument('--lambda-name', default='dev_audio_transcribe',
                        help='Name of the Lambda function')
    
    args = parser.parse_args()
    
    # Run the test
    test = TranscribeE2ETest(
        input_bucket=args.input_bucket,
        output_bucket=args.output_bucket,
        region=args.region,
        lambda_name=args.lambda_name
    )
    
    success = test.run_test()
    
    # Exit with appropriate code for CI/CD integration
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 