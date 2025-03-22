import json
import os
import boto3
import pytest
from moto import mock_s3, mock_sqs
from src.handlers.chunking_handler import lambda_handler

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="function")
def s3_client(aws_credentials):
    """Create a mock S3 client."""
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-transcription-bucket')
        yield s3

@pytest.fixture(scope="function")
def sqs_client(aws_credentials):
    """Create a mock SQS client."""
    with mock_sqs():
        sqs = boto3.client('sqs', region_name='us-east-1')
        queue_url = sqs.create_queue(QueueName='test-chunks-queue')['QueueUrl']
        yield sqs

@pytest.fixture
def test_bucket():
    """Return the test bucket name."""
    return 'test-transcription-bucket'

@pytest.fixture
def test_queue():
    """Return the test queue URL."""
    return 'https://sqs.us-east-1.amazonaws.com/123456789012/test-chunks-queue'

@pytest.fixture
def sample_transcription_result():
    """Return a sample transcription result."""
    return {
        "transcription_text": "This is a test transcription.",
        "audio_segments": [
            {
                "id": 0,
                "transcript": "This is the first test segment.",
                "start_time": "0.0",
                "end_time": "10.0",
                "items": [0, 1, 2, 3, 4]
            },
            {
                "id": 1,
                "transcript": "This is the second test segment.",
                "start_time": "10.0",
                "end_time": "20.0",
                "items": [5, 6, 7, 8, 9]
            }
        ]
    }

def test_end_to_end_processing(s3_client, sqs_client, test_bucket, test_queue, sample_transcription_result):
    """Test end-to-end processing of transcription results."""
    # Setup: Upload test file to S3
    key = "test/transcription-result.json"
    s3_client.put_object(
        Bucket=test_bucket,
        Key=key,
        Body=json.dumps(sample_transcription_result)
    )

    # Set environment variables
    os.environ["SQS_QUEUE_URL"] = test_queue

    # Create the event in EventBridge format
    event = {
        "detail": {
            "records": [{
                "s3": {
                    "bucket": {"name": test_bucket},
                    "object": {"key": key}
                }
            }]
        }
    }

    # Process the event
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200

    # Verify the response
    response_body = json.loads(response["body"])
    assert "message" in response_body
    assert "Chunking completed successfully" in response_body["message"]
    assert response_body["segments_sent"] == 2

def test_error_handling_missing_file(s3_client, sqs_client, test_bucket, test_queue):
    """Test error handling when S3 file is missing."""
    event = {
        "detail": {
            "records": [{
                "s3": {
                    "bucket": {"name": test_bucket},
                    "object": {"key": "nonexistent.json"}
                }
            }]
        }
    }

    os.environ["SQS_QUEUE_URL"] = test_queue

    response = lambda_handler(event, {})
    assert response["statusCode"] == 500
    error_body = json.loads(response["body"])
    assert "error" in error_body
    assert "File nonexistent.json not found" in error_body["error"]

def test_error_handling_invalid_json(s3_client, sqs_client, test_bucket, test_queue):
    """Test error handling with invalid JSON in S3."""
    key = "invalid.json"
    s3_client.put_object(
        Bucket=test_bucket,
        Key=key,
        Body="invalid json content"
    )

    event = {
        "detail": {
            "records": [{
                "s3": {
                    "bucket": {"name": test_bucket},
                    "object": {"key": key}
                }
            }]
        }
    }

    os.environ["SQS_QUEUE_URL"] = test_queue

    response = lambda_handler(event, {})
    assert response["statusCode"] == 500
    error_body = json.loads(response["body"])
    assert "error" in error_body
    assert "File invalid.json is not valid JSON" in error_body["error"] 