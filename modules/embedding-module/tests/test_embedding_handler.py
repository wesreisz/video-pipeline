import json
import pytest
from unittest.mock import Mock, patch

from src.handlers.embedding_handler import lambda_handler
from src.services.openai_service import OpenAIService
from src.services.pinecone_service import PineconeService

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

@pytest.fixture
def mock_openai_service():
    """Fixture for mocked OpenAI service."""
    with patch('src.handlers.embedding_handler.OpenAIService') as mock:
        service = Mock()
        service.create_embedding.return_value = [0.0] * 1536  # Mocked embedding vector
        mock.return_value = service
        yield service

@pytest.fixture
def mock_pinecone_service():
    """Fixture for mocked Pinecone service."""
    with patch('src.handlers.embedding_handler.PineconeService') as mock:
        service = Mock()
        service.upsert_embeddings.return_value = None
        mock.return_value = service
        yield service

def test_successful_processing(sqs_event, mock_openai_service, mock_pinecone_service):
    """Test successful processing of an SQS message."""
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response structure
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1
    assert body['processed_records'][0]['status'] == 'success'
    assert body['processed_records'][0]['chunk_id'] == 'test-chunk-123'
    
    # Verify service calls
    mock_openai_service.create_embedding.assert_called_once_with(
        "This is a sample text for embedding generation."
    )
    mock_pinecone_service.upsert_embeddings.assert_called_once_with(
        'test-chunk-123',
        [0.0] * 1536,
        {'text': "This is a sample text for embedding generation."}
    )

def test_missing_required_fields(sqs_event, mock_openai_service, mock_pinecone_service):
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
    
    # Verify no service calls were made
    mock_openai_service.create_embedding.assert_not_called()
    mock_pinecone_service.upsert_embeddings.assert_not_called()

def test_openai_service_error(sqs_event, mock_openai_service, mock_pinecone_service):
    """Test handling of OpenAI service errors."""
    # Configure OpenAI service to raise an exception
    mock_openai_service.create_embedding.side_effect = Exception("OpenAI API error")
    
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1
    assert body['processed_records'][0]['status'] == 'error'
    assert 'OpenAI API error' in body['processed_records'][0]['error']
    
    # Verify Pinecone service was not called
    mock_pinecone_service.upsert_embeddings.assert_not_called()

def test_empty_event(mock_openai_service, mock_pinecone_service):
    """Test handling of an empty event."""
    # Call the lambda handler with an empty event
    response = lambda_handler({"Records": []}, {})
    
    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 0
    
    # Verify no service calls were made
    mock_openai_service.create_embedding.assert_not_called()
    mock_pinecone_service.upsert_embeddings.assert_not_called()

def test_pinecone_service_error(sqs_event, mock_openai_service, mock_pinecone_service):
    """Test handling of Pinecone service errors."""
    # Configure Pinecone service to raise an exception
    mock_pinecone_service.upsert_embeddings.side_effect = Exception("Pinecone API error")
    
    # Call the lambda handler
    response = lambda_handler(sqs_event, {})
    
    # Assert the response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Embedding process completed'
    assert len(body['processed_records']) == 1
    assert body['processed_records'][0]['status'] == 'error'
    assert 'Pinecone API error' in body['processed_records'][0]['error']
    
    # Verify OpenAI service was called but failed at Pinecone
    mock_openai_service.create_embedding.assert_called_once() 