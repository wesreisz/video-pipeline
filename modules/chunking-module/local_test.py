#!/usr/bin/env python
"""
Local test script for the chunking module.
This script simulates an S3 event to test the chunking module locally.
"""
import json
import os
import sys
import uuid
from datetime import datetime

# Add the project root to the Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Add the current directory to the path so imports work correctly
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the Lambda handler and services
try:
    from src.handlers.chunking_handler import lambda_handler
    from src.services.chunking_service import ChunkingService
    from src.services.transcription_loader_service import TranscriptionLoaderService
except ImportError as e:
    print(f"Import error: {e}")
    print("Attempting to fix imports...")
    try:
        # Try different import paths
        from modules.chunking_module.src.services.chunking_service import ChunkingService
        from modules.chunking_module.src.services.transcription_loader_service import TranscriptionLoaderService
        # Lambda handler might not be available or needed for testing
        lambda_handler = None
    except ImportError as e:
        print(f"Still having import issues: {e}")
        print("Continuing with basic testing...")

def create_test_transcription_file():
    """Create a sample transcription JSON file for testing."""
    timestamp = datetime.now().isoformat()
    test_data = {
        "original_file": "sample.mp3",
        "transcription_text": "This is a sample transcription for testing the chunking module. It includes audio segments that represent sentences or logical divisions in the audio.",
        "timestamp": timestamp,
        "job_name": f"test-job-{uuid.uuid4()}",
        "media_type": "audio",
        "segments": [
            {
                "start_time": 0.0,
                "end_time": 2.5,
                "text": "This is"
            },
            {
                "start_time": 2.5,
                "end_time": 5.0,
                "text": "a sample transcription"
            },
            {
                "start_time": 5.0,
                "end_time": 7.5,
                "text": "for testing the chunking module."
            },
            {
                "start_time": 7.5,
                "end_time": 10.0,
                "text": "It includes audio segments"
            },
            {
                "start_time": 10.0,
                "end_time": 15.0,
                "text": "that represent sentences or logical divisions in the audio."
            }
        ],
        "audio_segments": [
            {
                "start_time": 0.0,
                "end_time": 5.0,
                "text": "This is a sample transcription",
                "confidence": 0.95
            },
            {
                "start_time": 5.0,
                "end_time": 10.0,
                "text": "for testing the chunking module. It includes audio segments",
                "confidence": 0.92
            },
            {
                "start_time": 10.0,
                "end_time": 15.0,
                "text": "that represent sentences or logical divisions in the audio.",
                "confidence": 0.88
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
    os.environ["CHUNKING_OUTPUT_BUCKET"] = "placeholder-bucket"
    
    # 1. Create a test transcription file
    print("Creating test transcription file...")
    transcription_file = create_test_transcription_file()
    
    # 2. Create a simulated S3 event
    print("Creating simulated S3 event...")
    bucket = "dev-media-transcribe-output"
    key = "transcriptions/test_transcription.json"
    event = create_s3_event(bucket, key)
    
    # 3. Test our new TranscriptionLoaderService and ChunkingService directly
    print("\nTesting TranscriptionLoaderService and ChunkingService directly...")
    try:
        # Create an instance of ChunkingService
        chunking_service = ChunkingService()
        
        # Process the local test file
        print(f"Processing local file: {transcription_file}")
        segments_dict = chunking_service.process_local_file(transcription_file)
        
        # Print the results
        print("\nResults from direct service test:")
        print(f"Number of segments: {segments_dict['segments_count']}")
        print(f"Total duration: {segments_dict.get('total_duration', 0):.2f} seconds")
        print("\nFirst audio segment:")
        if segments_dict['segments']:
            first_segment = segments_dict['segments'][0]
            print(f"  Start time: {first_segment['start_time']}")
            print(f"  End time: {first_segment['end_time']}")
            print(f"  Text: \"{first_segment['text']}\"")
            print(f"  Confidence: {first_segment.get('confidence', 'N/A')}")
        
        print("\n✅ Direct service test completed successfully")
    except Exception as e:
        print(f"\n❌ Direct service test failed: {str(e)}")
    
    # 4. Call the Lambda handler with the event
    print("\nCalling Lambda handler...")
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
            mock_process.return_value = {
                "segments_count": 3,
                "total_duration": 15.0,
                "segments": [
                    # Simplified segments for the mock
                    {"start_time": 0.0, "end_time": 5.0, "text": "This is a sample transcription"}
                ]
            }
            
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