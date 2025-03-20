#!/usr/bin/env python3
"""
Direct test for the chunking module.

This script directly invokes the chunking module with a transcription file from S3,
bypassing the Step Functions workflow to test if the chunking module itself works correctly.

Usage:
    python test_chunking.py --bucket BUCKET_NAME --key KEY_NAME

Example:
    python test_chunking.py --bucket dev-media-transcribe-output --key transcriptions/hello-my_name_is_wes_25dc0df8.json
"""

import sys
import os
import json
import logging
import argparse
import boto3
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_chunking')

# Add the src directory to sys.path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Try to import our chunking modules
try:
    from services.chunking_service import ChunkingService
    from handlers.chunking_handler import lambda_handler
    logger.info("Successfully imported chunking modules")
except ImportError as e:
    logger.error(f"Failed to import chunking modules: {e}")
    sys.exit(1)

def create_s3_event(bucket, key):
    """Create a simulated S3 event that looks like what the chunking module expects from Step Functions."""
    return {
        "Records": [
            {
                "eventVersion": "2.1",
                "eventSource": "aws:s3",
                "awsRegion": "us-east-1",
                "eventTime": datetime.now().isoformat(),
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "test-request-id",
                    "x-amz-id-2": "EXAMPLE"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": bucket,
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": f"arn:aws:s3:::{bucket}"
                    },
                    "object": {
                        "key": key,
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }

def create_step_functions_event(bucket, key):
    """Create a simulated event that looks like what the chunking module expects from Step Functions."""
    return {
        "detail": {
            "records": [
                {
                    "s3": {
                        "bucket": {
                            "name": bucket
                        },
                        "object": {
                            "key": key
                        }
                    }
                }
            ]
        }
    }
    
def test_chunking_service(s3_bucket, s3_key):
    """Test the ChunkingService directly."""
    logger.info(f"Testing ChunkingService directly with bucket={s3_bucket}, key={s3_key}")
    
    try:
        # Create an instance of ChunkingService
        chunking_service = ChunkingService()
        
        # Process the transcription file
        logger.info(f"Processing transcription file: {s3_bucket}/{s3_key}")
        result = chunking_service.process_media(s3_bucket, s3_key)
        
        # Check the result
        if result:
            logger.info("ChunkingService returned a result")
            logger.info(f"Result segments count: {result.get('segments_count', 0)}")
            
            # Ensure total_duration is a float before formatting
            total_duration = result.get('total_duration', 0)
            if isinstance(total_duration, str):
                total_duration = float(total_duration)
            logger.info(f"Result total duration: {total_duration:.2f}s")
            
            # Display some sample segments if available
            segments = result.get('segments', [])
            if segments:
                logger.info("\nSample segments:")
                for i, segment in enumerate(segments[:3]):  # Show first 3 segments
                    # Ensure start_time and end_time are floats before formatting
                    start_time = segment.get('start_time', 0)
                    if isinstance(start_time, str):
                        start_time = float(start_time)
                    
                    end_time = segment.get('end_time', 0)
                    if isinstance(end_time, str):
                        end_time = float(end_time)
                    
                    logger.info(f"  Segment {i+1}: {start_time:.2f}s - {end_time:.2f}s")
                    logger.info(f"  Text: \"{segment.get('text', segment.get('transcript', 'N/A'))}\"")
                    
                if len(segments) > 3:
                    logger.info(f"  ... and {len(segments) - 3} more segments")
            else:
                logger.error("No segments found in result")
                
            return True
        else:
            logger.error("ChunkingService returned no result")
            return False
            
    except Exception as e:
        logger.error(f"Error testing ChunkingService: {e}")
        return False

def test_lambda_handler(s3_bucket, s3_key):
    """Test the chunking Lambda handler."""
    logger.info(f"Testing lambda_handler with bucket={s3_bucket}, key={s3_key}")
    
    try:
        # Create a simulated S3 event
        event = create_s3_event(s3_bucket, s3_key)
        
        # Create a simulated context
        class MockContext:
            def __init__(self):
                self.function_name = "test_chunking"
                self.memory_limit_in_mb = 128
                self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test_chunking"
                self.aws_request_id = "test-request-id"
                
        context = MockContext()
        
        # Call the Lambda handler
        logger.info("Calling lambda_handler with S3 event")
        response = lambda_handler(event, context)
        
        # Check the response
        if response:
            logger.info("Lambda handler returned a response")
            logger.info(f"Status code: {response.get('statusCode')}")
            
            # Parse the response body if it's a JSON string
            body = response.get('body')
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except json.JSONDecodeError:
                    pass
                    
            if isinstance(body, dict):
                logger.info(f"Message: {body.get('message')}")
                logger.info(f"Segments count: {body.get('segments_count')}")
                logger.info(f"Total duration: {body.get('total_duration')}s")
                
            # Now test with a Step Functions style event
            step_event = create_step_functions_event(s3_bucket, s3_key)
            logger.info("\nCalling lambda_handler with Step Functions event")
            step_response = lambda_handler(step_event, context)
            
            if step_response:
                logger.info("Lambda handler returned a response for Step Functions event")
                logger.info(f"Status code: {step_response.get('statusCode')}")
                
                # Parse the response body if it's a JSON string
                step_body = step_response.get('body')
                if isinstance(step_body, str):
                    try:
                        step_body = json.loads(step_body)
                    except json.JSONDecodeError:
                        pass
                        
                if isinstance(step_body, dict):
                    logger.info(f"Message: {step_body.get('message')}")
                    logger.info(f"Segments count: {step_body.get('segments_count')}")
                    logger.info(f"Total duration: {step_body.get('total_duration')}s")
            else:
                logger.error("Lambda handler returned no response for Step Functions event")
                
            return True
        else:
            logger.error("Lambda handler returned no response")
            return False
            
    except Exception as e:
        logger.error(f"Error testing lambda_handler: {e}")
        return False
        

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test the chunking module directly')
    parser.add_argument('--bucket', required=True, help='S3 bucket containing the transcription file')
    parser.add_argument('--key', required=True, help='S3 key of the transcription file')
    return parser.parse_args()

def main():
    """Main function to run the tests."""
    args = parse_args()
    
    logger.info(f"Starting chunking module tests for bucket={args.bucket}, key={args.key}")
    
    # Test the ChunkingService directly
    service_success = test_chunking_service(args.bucket, args.key)
    
    # Test the Lambda handler
    handler_success = test_lambda_handler(args.bucket, args.key)
    
    # Report overall success/failure
    if service_success and handler_success:
        logger.info("\n✅ All chunking module tests PASSED!")
        return 0
    else:
        logger.error("\n❌ Some chunking module tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 