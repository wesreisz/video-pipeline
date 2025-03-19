#!/usr/bin/env python
"""
Local test script for the chunking module.
This script simulates an S3 event to test the chunking module locally.
"""
import json
import os
import uuid
from datetime import datetime

# Import the Lambda handler
from src.handlers.chunking_handler import lambda_handler

def create_test_transcription_file():
    """Create a sample transcription JSON file for testing."""
    timestamp = datetime.now().isoformat()
    test_data = {
        "original_file": "sample.mp3",
        "transcription_text": "This is a sample transcription for testing the chunking module.",
        "timestamp": timestamp,
        "job_name": f"test-job-{uuid.uuid4()}",
        "media_type": "audio",
        "segments": [
            {
                "start_time": 0.0,
                "end_time": 5.0,
                "text": "This is a sample transcription"
            },
            {
                "start_time": 5.0,
                "end_time": 10.0,
                "text": "for testing the chunking module."
            }
        ]
    }
    
    # Create a temporary directory if it doesn't exist
    os.makedirs("tmp", exist_ok=True)
    
    # Write the test data to a file
    file_path = "tmp/test_transcription.json"
    with open(file_path, "w") as f:
        json.dump(test_data, f, indent=2)
    
    return file_path

def create_s3_event(bucket, key):
    """Create a simulated S3 event."""
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
                    "x-amz-request-id": str(uuid.uuid4()),
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

def main():
    """Main function to run the local test."""
    # Set up test environment
    os.environ["CHUNKING_OUTPUT_BUCKET"] = "dev-media-chunking-output"
    
    # 1. Create a test transcription file
    print("Creating test transcription file...")
    transcription_file = create_test_transcription_file()
    
    # 2. Create a simulated S3 event
    print("Creating simulated S3 event...")
    bucket = "dev-media-transcribe-output"
    key = "transcriptions/test_transcription.json"
    event = create_s3_event(bucket, key)
    
    # 3. Call the Lambda handler with the event
    print("Calling Lambda handler...")
    context = type('obj', (object,), {
        'function_name': 'local-test',
        'memory_limit_in_mb': 128,
        'invoked_function_arn': 'arn:aws:lambda:us-east-1:123456789012:function:local-test',
        'aws_request_id': str(uuid.uuid4()),
    })
    
    try:
        # Mock the ChunkingService to avoid actual S3 operations
        from unittest.mock import patch
        with patch('src.services.chunking_service.ChunkingService.process_media') as mock_process:
            # Configure the mock to return a reasonable value
            mock_process.return_value = f"chunks/test_transcription-chunks.json"
            
            # Call the handler
            response = lambda_handler(event, context)
            
            # Print the response
            print("\nLambda Response:")
            print(json.dumps(response, indent=2))
            
            # Verify the response
            if response['statusCode'] == 200:
                print("\n✅ Test PASSED: Lambda handler executed successfully")
                body = json.loads(response['body'])
                print(f"Output file: {body.get('output_file')}")
            else:
                print("\n❌ Test FAILED: Lambda handler returned an error")
                print(f"Error: {response['body']}")
    
    except Exception as e:
        print(f"\n❌ Test FAILED: An error occurred: {str(e)}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 