import json
import pytest
from unittest.mock import patch, Mock
from handlers.question_handler import lambda_handler, QuestionRequest

@patch('handlers.question_handler._secrets_service')
@patch('handlers.question_handler._auth_util')
@patch('handlers.question_handler.OpenAI')
@patch('handlers.question_handler.Pinecone')
def test_basic_request_handling(mock_pinecone, mock_openai, mock_auth, mock_secrets):
    """Test basic request handling without testing OpenAI/Pinecone integration."""
    # Arrange
    mock_secrets.get_api_key.return_value = 'test-api-key'
    mock_auth.is_authorized.return_value = True
    
    # Mock OpenAI response
    mock_openai_client = Mock()
    mock_openai_client.embeddings.create.return_value = Mock(
        data=[Mock(embedding=[0.1] * 1536)]
    )
    mock_openai.return_value = mock_openai_client
    
    # Mock Pinecone response
    mock_index = Mock()
    mock_index.query.return_value = {
        'matches': [
            {
                'metadata': {
                    'text': 'Sample text 1',
                    'title': 'Test Title 1',
                    'timestamp': '00:00:00'
                }
            }
        ]
    }
    mock_pinecone_client = Mock()
    mock_pinecone_client.Index.return_value = mock_index
    mock_pinecone.return_value = mock_pinecone_client
    
    test_event = {
        'body': json.dumps({
            'question': 'What is the capital of France?',
            'email': 'test@example.com'
        }),
        'headers': {
            'x-api-key': 'test-api-key'
        }
    }
    
    # Act
    result = lambda_handler(test_event, None)
    
    # Assert
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert 'pinecone_matches' in body
    assert len(body['pinecone_matches']) > 0

@patch('handlers.question_handler._secrets_service')
@patch('handlers.question_handler._auth_util')
def test_missing_body(mock_auth, mock_secrets):
    """Test handling of request with missing body."""
    # Arrange
    mock_secrets.get_api_key.return_value = 'test-api-key'
    mock_auth.is_authorized.return_value = True
    
    test_event = {
        'headers': {
            'x-api-key': 'test-api-key'
        }
    }
    
    # Act
    result = lambda_handler(test_event, None)
    
    # Assert
    assert result['statusCode'] == 400
    body = json.loads(result['body'])
    assert 'error' in body

@patch('handlers.question_handler._secrets_service')
@patch('handlers.question_handler._auth_util')
@patch('handlers.question_handler.OpenAI')
@patch('handlers.question_handler.Pinecone')
def test_successful_question_processing(mock_pinecone, mock_openai, mock_auth, mock_secrets):
    """Test successful question processing with mocked OpenAI and Pinecone."""
    # Arrange
    mock_secrets.get_api_key.return_value = 'test-api-key'
    mock_auth.is_authorized.return_value = True
    
    # Mock OpenAI response
    mock_openai_client = Mock()
    mock_openai_client.embeddings.create.return_value = Mock(
        data=[Mock(embedding=[0.1] * 1536)]
    )
    mock_openai.return_value = mock_openai_client
    
    # Mock Pinecone response
    mock_index = Mock()
    mock_index.query.return_value = {
        'matches': [
            {
                'metadata': {
                    'text': 'Sample text 1',
                    'title': 'Test Title 1',
                    'timestamp': '00:00:00'
                }
            }
        ]
    }
    mock_pinecone_client = Mock()
    mock_pinecone_client.Index.return_value = mock_index
    mock_pinecone.return_value = mock_pinecone_client
    
    test_event = {
        'body': json.dumps({
            'question': 'What is the capital of France?',
            'email': 'test@example.com'
        }),
        'headers': {
            'x-api-key': 'test-api-key'
        }
    }
    
    # Act
    result = lambda_handler(test_event, None)
    
    # Assert
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert 'pinecone_matches' in body
    assert len(body['pinecone_matches']) > 0 