#!/usr/bin/env python3
"""
Pytest test file for the chunking module.

This module contains pytest tests for the chunking service and lambda handler.
"""

import os
import json
import logging
import pytest
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_chunking')

# Import our chunking modules
from services.chunking_service import ChunkingService
from handlers.chunking_handler import lambda_handler

# Define fixtures specific to this test file
@pytest.fixture(scope="module")
def s3_event(s3_bucket, s3_key):
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
                    "x-amz-request-id": "test-request-id",
                    "x-amz-id-2": "EXAMPLE"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": s3_bucket,
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": f"arn:aws:s3:::{s3_bucket}"
                    },
                    "object": {
                        "key": s3_key,
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }

@pytest.fixture(scope="module")
def step_functions_event(s3_bucket, s3_key):
    """Create a simulated Step Functions event."""
    return {
        "detail": {
            "records": [
                {
                    "s3": {
                        "bucket": {
                            "name": s3_bucket
                        },
                        "object": {
                            "key": s3_key
                        }
                    }
                }
            ]
        }
    }

@pytest.fixture(scope="module")
def lambda_context():
    """Create a mock Lambda context."""
    class MockContext:
        def __init__(self):
            self.function_name = "test_chunking"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test_chunking"
            self.aws_request_id = "test-request-id"
    
    return MockContext()

@pytest.mark.integration
def test_chunking_service(s3_bucket, s3_key):
    """Test the ChunkingService directly."""
    logger.info(f"Testing ChunkingService directly with bucket={s3_bucket}, key={s3_key}")
    
    # Skip test if bucket or key not provided
    if not s3_bucket or not s3_key:
        pytest.skip("Skipping test_chunking_service: bucket or key not provided")
    
    # Create an instance of ChunkingService
    chunking_service = ChunkingService()
    
    # Process the transcription file
    logger.info(f"Processing transcription file: {s3_bucket}/{s3_key}")
    result = chunking_service.process_media(s3_bucket, s3_key)
    
    # Verify the result
    assert result is not None, "ChunkingService returned no result"
    assert 'segments_count' in result, "Result missing segments_count"
    assert 'total_duration' in result, "Result missing total_duration"
    assert 'segments' in result, "Result missing segments"
    
    # Log some information about the results
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
            # Log segment details
            start_time = float(segment.get('start_time', 0)) if isinstance(segment.get('start_time', 0), str) else segment.get('start_time', 0)
            end_time = float(segment.get('end_time', 0)) if isinstance(segment.get('end_time', 0), str) else segment.get('end_time', 0)
            
            logger.info(f"  Segment {i+1}: {start_time:.2f}s - {end_time:.2f}s")
            logger.info(f"  Text: \"{segment.get('text', segment.get('transcript', 'N/A'))}\"")
    
    # Verify that segments are properly structured
    for segment in segments[:5]:  # Check first 5 segments
        assert 'start_time' in segment, "Segment missing start_time"
        assert 'end_time' in segment, "Segment missing end_time"
        assert 'text' in segment or 'transcript' in segment, "Segment missing text/transcript"

@pytest.mark.integration
def test_lambda_handler_with_s3_event(s3_bucket, s3_key, s3_event, lambda_context):
    """Test the chunking Lambda handler with an S3 event."""
    # Skip test if bucket or key not provided
    if not s3_bucket or not s3_key:
        pytest.skip("Skipping test_lambda_handler: bucket or key not provided")
    
    logger.info(f"Testing lambda_handler with S3 event: bucket={s3_bucket}, key={s3_key}")
    
    # Call the Lambda handler
    response = lambda_handler(s3_event, lambda_context)
    
    # Verify the response
    assert response is not None, "Lambda handler returned no response"
    assert response.get('statusCode') == 200, f"Expected status code 200, got {response.get('statusCode')}"
    
    # Log the response for information
    logger.info(f"Lambda handler response: {json.dumps(response, indent=2)}")
    
    # If the body is a string, try to parse it as JSON
    body = response.get('body')
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
    
    # Additional assertions based on expected response structure
    if isinstance(body, dict):
        assert 'message' in body, "Response body missing 'message'"
        if 'segments_count' in body:
            assert isinstance(body['segments_count'], int), "segments_count should be an integer"
        if 'total_duration' in body:
            assert isinstance(body['total_duration'], (int, float)) or \
                  (isinstance(body['total_duration'], str) and body['total_duration'].replace('.', '', 1).isdigit()), \
                  "total_duration should be a number"

@pytest.mark.integration
def test_lambda_handler_with_step_functions_event(s3_bucket, s3_key, step_functions_event, lambda_context):
    """Test the chunking Lambda handler with a Step Functions event."""
    # Skip test if bucket or key not provided
    if not s3_bucket or not s3_key:
        pytest.skip("Skipping test_lambda_handler_step_functions: bucket or key not provided")
    
    logger.info(f"Testing lambda_handler with Step Functions event: bucket={s3_bucket}, key={s3_key}")
    
    # Call the Lambda handler
    response = lambda_handler(step_functions_event, lambda_context)
    
    # Verify the response
    assert response is not None, "Lambda handler returned no response"
    
    # Log the response for information
    logger.info(f"Lambda handler response: {json.dumps(response, indent=2)}") 