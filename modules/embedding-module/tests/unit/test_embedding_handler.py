import json
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Ensure path is set correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../../src'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    
# Import after fixing path
from handlers.embedding_handler import lambda_handler, get_openai_service
from services.openai_service import OpenAIService, OpenAIServiceError, EmbeddingResponse

@pytest.fixture
def mock_openai_service():
    """Fixture to create a mock OpenAI service"""
    with patch('handlers.embedding_handler._openai_service') as mock_service:
        yield mock_service

@pytest.fixture
def sample_event():
    """Fixture to create a sample SQS event"""
    return {
        'Records': [
            {
                'body': json.dumps({
                    'chunk_id': 'test_chunk_1',
                    'text': 'This is a test chunk',
                    'start_time': 0,
                    'end_time': 10
                })
            },
            {
                'body': json.dumps({
                    'chunk_id': 'test_chunk_2',
                    'text': 'This is another test chunk',
                    'start_time': 10,
                    'end_time': 20
                })
            }
        ]
    }

@pytest.fixture
def mock_embedding_response():
    """Fixture to create a sample embedding response"""
    return EmbeddingResponse(
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
        model="text-embedding-ada-002",
        usage={
            "prompt_tokens": 10,
            "total_tokens": 10
        }
    )

def test_successful_embedding_creation(mock_openai_service, sample_event, mock_embedding_response):
    """Test successful processing of chunks and embedding creation"""
    # Configure mock to return sample embedding response
    mock_openai_service.create_embedding.return_value = mock_embedding_response

    # Call lambda handler
    response = lambda_handler(sample_event, {})

    # Verify response structure and status code
    assert response['statusCode'] == 200
    
    # Parse response body
    body = json.loads(response['body'])
    assert 'message' in body
    assert 'processed_records' in body
    
    # Verify all records were processed
    processed_records = body['processed_records']
    assert len(processed_records) == 2
    
    # Verify first record details
    first_record = processed_records[0]
    assert first_record['chunk_id'] == 'test_chunk_1'
    assert first_record['status'] == 'success'
    assert first_record['embedding'] == mock_embedding_response.embedding
    assert first_record['model'] == mock_embedding_response.model
    assert first_record['usage'] == mock_embedding_response.usage

    # Verify OpenAI service was called correctly
    assert mock_openai_service.create_embedding.call_count == 2
    mock_openai_service.create_embedding.assert_any_call('This is a test chunk')
    mock_openai_service.create_embedding.assert_any_call('This is another test chunk')

def test_openai_service_error(mock_openai_service, sample_event):
    """Test handling of OpenAI service errors"""
    # Configure mock to raise OpenAI service error
    mock_openai_service.create_embedding.side_effect = OpenAIServiceError("API error")

    # Call lambda handler
    response = lambda_handler(sample_event, {})

    # Verify response structure and status code
    assert response['statusCode'] == 200
    
    # Parse response body
    body = json.loads(response['body'])
    processed_records = body['processed_records']
    
    # Verify error handling for all records
    assert len(processed_records) == 2
    for record in processed_records:
        assert record['status'] == 'error'
        assert 'OpenAI service error' in record['error']

def test_empty_event():
    """Test handling of empty event"""
    response = lambda_handler({'Records': []}, {})
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body['processed_records']) == 0

def test_malformed_event():
    """Test handling of malformed event data"""
    malformed_event = {
        'Records': [
            {
                'body': 'invalid json'
            }
        ]
    }
    
    response = lambda_handler(malformed_event, {})
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    processed_records = body['processed_records']
    assert len(processed_records) == 1
    assert processed_records[0]['status'] == 'error' 