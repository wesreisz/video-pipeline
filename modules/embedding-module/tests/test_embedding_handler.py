import json
import pytest
from unittest.mock import Mock, patch

from src.handlers.embedding_handler import lambda_handler

@pytest.fixture
def sqs_event():
    """Fixture for a sample SQS event."""
    return {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": json.dumps({
                    "chunk_id": "test-chunk-123",
                    "text": "This is a sample text for embedding generation."
                }),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                "awsRegion": "us-east-1"
            }
        ]
    }

def test_successful_processing(sqs_event):
    """Test successful processing of an SQS message."""
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response structure
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1

def test_missing_required_fields(sqs_event):
    """Test handling of messages with missing required fields."""
    # Modify the event to remove required fields
    sqs_event['Records'][0]['body'] = json.dumps({
        "some_other_field": "value"
    })
    
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1
    assert body['processed_records'][0]['status'] == 'error'

def test_empty_event():
    """Test handling of an empty event."""
    # Call the lambda handler with an empty event
    response = lambda_handler({"Records": []}, {})
    
    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 0

def test_malformed_json(sqs_event):
    """Test handling of malformed JSON in the message body."""
    # Set invalid JSON in the message body
    sqs_event['Records'][0]['body'] = "invalid json"
    
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1
    assert body['processed_records'][0]['status'] == 'error'