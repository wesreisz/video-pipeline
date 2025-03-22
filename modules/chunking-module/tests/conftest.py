import json
from typing import Dict, List
import pytest
from boto3.session import Session
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef
from mypy_boto3_sqs.type_defs import SendMessageBatchResultTypeDef

@pytest.fixture
def mock_aws_credentials():
    """Mocked AWS Credentials for moto."""
    return {
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_SECURITY_TOKEN": "testing",
        "AWS_SESSION_TOKEN": "testing",
        "AWS_DEFAULT_REGION": "us-east-1"
    }

@pytest.fixture
def sample_s3_event() -> Dict:
    """Sample S3 event fixture."""
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "test-bucket"
                    },
                    "object": {
                        "key": "test/transcription-result.json"
                    }
                }
            }
        ]
    }

@pytest.fixture
def sample_transcription_result() -> Dict:
    """Sample transcription result fixture."""
    return {
        "results": {
            "segments": [
                {
                    "start_time": 0.0,
                    "end_time": 10.0,
                    "text": "This is a test segment one."
                },
                {
                    "start_time": 10.0,
                    "end_time": 20.0,
                    "text": "This is a test segment two."
                }
            ]
        }
    }

@pytest.fixture
def mock_s3_response(sample_transcription_result) -> GetObjectOutputTypeDef:
    """Mock S3 get_object response fixture."""
    class MockBody:
        def read(self):
            return json.dumps(sample_transcription_result).encode()
    
    return {
        'Body': MockBody(),
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }

@pytest.fixture
def mock_sqs_response() -> SendMessageBatchResultTypeDef:
    """Mock SQS send_message_batch response fixture."""
    return {
        'Successful': [
            {
                'Id': 'test_message_1',
                'MessageId': 'test_message_id_1',
                'MD5OfMessageBody': 'test_md5_1'
            }
        ],
        'Failed': []
    } 