from unittest.mock import Mock, patch
import pytest
from openai import OpenAI
from openai.types.create_embedding_response import CreateEmbeddingResponse, Embedding, Usage

from services.openai_service import OpenAIService, OpenAIServiceError
from services.secrets_service import SecretsService

@pytest.fixture
def mock_secrets_service():
    """Create a mock secrets service."""
    mock = Mock(spec=SecretsService)
    mock.get_openai_api_key.return_value = "test-api-key"
    mock.get_openai_org_id.return_value = "test-org-id"
    mock.get_openai_base_url.return_value = "https://test.openai.com/v1"
    
    # Mock get_secret with a dictionary to handle different keys
    secret_values = {
        'openai_timeout': '20.0',
        'openai_max_retries': '3',
        'openai_model': 'text-embedding-ada-002'
    }
    mock.get_secret.side_effect = lambda x: secret_values.get(x)
    return mock

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    mock = Mock(spec=OpenAI)
    # Mock the embeddings.create method
    mock.embeddings = Mock()
    mock.embeddings.create.return_value = CreateEmbeddingResponse(
        data=[
            Embedding(
                embedding=[0.1, 0.2, 0.3],
                index=0,
                object="embedding"
            )
        ],
        model="text-embedding-ada-002",
        object="list",
        usage=Usage(
            prompt_tokens=10,
            total_tokens=10
        )
    )
    return mock

def test_init_with_valid_secrets(mock_secrets_service):
    """Test initialization with valid secrets."""
    service = OpenAIService(secrets_service=mock_secrets_service)
    assert service.api_key == "test-api-key"
    mock_secrets_service.get_openai_api_key.assert_called_once()

def test_init_without_api_key(mock_secrets_service):
    """Test initialization fails without API key."""
    mock_secrets_service.get_openai_api_key.return_value = None
    with pytest.raises(OpenAIServiceError, match="OpenAI API key not configured"):
        OpenAIService(secrets_service=mock_secrets_service)

def test_create_embedding_success(mock_openai_client):
    """Test successful embedding creation."""
    service = OpenAIService(client=mock_openai_client)
    response = service.create_embedding("test text")
    
    assert response.embedding == [0.1, 0.2, 0.3]
    assert response.model == "text-embedding-ada-002"
    assert response.usage == {
        "prompt_tokens": 10,
        "total_tokens": 10
    }
    
    mock_openai_client.embeddings.create.assert_called_once_with(
        model=OpenAIService.DEFAULT_MODEL,
        input="test text"
    )

def test_create_embedding_empty_text(mock_openai_client):
    """Test embedding creation with empty text fails."""
    service = OpenAIService(client=mock_openai_client)
    with pytest.raises(OpenAIServiceError, match="Input text cannot be empty"):
        service.create_embedding("")

def test_create_embedding_api_error(mock_openai_client):
    """Test handling of API errors."""
    mock_openai_client.embeddings.create.side_effect = Exception("API Error")
    service = OpenAIService(client=mock_openai_client)
    
    with pytest.raises(OpenAIServiceError, match="Unexpected error during embedding creation"):
        service.create_embedding("test text") 