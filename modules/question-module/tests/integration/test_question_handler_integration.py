import pytest
from unittest.mock import Mock, patch
import json
from handlers.question_handler import (
    QuestionRequest,
    lambda_handler,
    ValidationError,
    AuthorizationError,
    ConfigurationError,
    QuestionProcessingError
)

# Mock responses
MOCK_EMBEDDING_RESPONSE = Mock(
    data=[Mock(embedding=[0.1] * 1536)]  # OpenAI uses 1536-dimensional embeddings
)

MOCK_PINECONE_RESPONSE = {
    'matches': [
        {
            'metadata': {
                'text': 'Sample text 1',
                'title': 'Test Title 1',
                'timestamp': '00:00:00'
            }
        },
        {
            'metadata': {
                'text': 'Sample text 2',
                'title': 'Test Title 2',
                'timestamp': '00:01:00'
            }
        }
    ]
}

@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    with patch('handlers.question_handler.OpenAI') as mock:
        client = Mock()
        client.embeddings.create.return_value = MOCK_EMBEDDING_RESPONSE
        mock.return_value = client
        yield mock

@pytest.fixture
def mock_pinecone():
    """Mock Pinecone client"""
    with patch('handlers.question_handler.Pinecone') as mock:
        index = Mock()
        index.query.return_value = MOCK_PINECONE_RESPONSE
        client = Mock()
        client.Index.return_value = index
        mock.return_value = client
        yield mock

@pytest.fixture
def mock_secrets():
    """Mock secrets service"""
    with patch('handlers.question_handler._secrets_service') as mock:
        mock.get_api_key.return_value = 'test-api-key'
        mock.get_secret.side_effect = lambda key: {
            'openai_api_key': 'test-openai-key',
            'pinecone_api_key': 'test-pinecone-key'
        }.get(key)
        yield mock

@pytest.fixture
def mock_auth():
    """Mock auth utility"""
    with patch('handlers.question_handler._auth_util') as mock:
        mock.is_authorized.return_value = True
        yield mock

@pytest.fixture
def valid_event():
    """Create a valid Lambda event"""
    return {
        'headers': {'x-api-key': 'test-api-key'},
        'body': json.dumps({
            'question': 'What is the main topic?',
            'email': 'test@example.com'
        })
    }

class TestQuestionHandlerIntegration:
    def test_successful_question_processing(
        self, valid_event, mock_openai, mock_pinecone, mock_secrets, mock_auth
    ):
        """Test successful end-to-end question processing"""
        response = lambda_handler(valid_event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'pinecone_matches' in body
        assert len(body['pinecone_matches']) == 2
        
        # Verify service calls
        mock_openai.return_value.embeddings.create.assert_called_once()
        mock_pinecone.return_value.Index.assert_called_once_with('talk-embeddings')

    def test_invalid_api_key(
        self, valid_event, mock_secrets
    ):
        """Test handling of invalid API key"""
        event = valid_event.copy()
        event['headers']['x-api-key'] = 'invalid-key'
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Invalid API key' in body['error']

    def test_invalid_request_body(
        self, valid_event, mock_secrets
    ):
        """Test handling of invalid request body"""
        event = valid_event.copy()
        event['body'] = json.dumps({})  # Empty body
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'Missing required fields' in body['error']

    def test_unauthorized_email(
        self, valid_event, mock_secrets, mock_auth
    ):
        """Test handling of unauthorized email"""
        mock_auth.is_authorized.return_value = False
        
        response = lambda_handler(valid_event, None)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'not authorized' in body['error']

    def test_openai_service_error(
        self, valid_event, mock_openai, mock_secrets, mock_auth
    ):
        """Test handling of OpenAI service error"""
        mock_openai.return_value.embeddings.create.side_effect = Exception('OpenAI Error')
        
        response = lambda_handler(valid_event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body

    def test_pinecone_service_error(
        self, valid_event, mock_openai, mock_pinecone, mock_secrets, mock_auth
    ):
        """Test handling of Pinecone service error"""
        mock_pinecone.return_value.Index.side_effect = Exception('Pinecone Error')
        
        response = lambda_handler(valid_event, None)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body 