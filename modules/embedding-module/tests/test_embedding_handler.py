import json
import pytest
from unittest.mock import Mock, patch

from src.handlers.embedding_handler import lambda_handler

@pytest.fixture
def sqs_event() -> dict:
    """
    Fixture for a sample SQS event.
    
    Returns:
        dict: A properly formatted SQS event with test data
    """
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

@patch('src.handlers.embedding_handler.OpenAIService')
@patch('src.handlers.embedding_handler.PineconeService')
def test_successful_processing(mock_pinecone_service, mock_openai_service, sqs_event):
    """
    Test successful processing of an SQS message with mocked services.
    
    Args:
        mock_pinecone_service: Mocked PineconeService class
        mock_openai_service: Mocked OpenAIService class
        sqs_event: Test event fixture
    """
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response structure and status
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1
