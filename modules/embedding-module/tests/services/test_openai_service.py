import pytest
from unittest.mock import Mock, patch
from src.services.openai_service import OpenAIService, OpenAIServiceError, EmbeddingResponse

@pytest.fixture
def mock_openai_client():
    client = Mock()
    return client

@pytest.fixture
def openai_service(mock_openai_client):
    return OpenAIService(client=mock_openai_client)

def test_create_embedding_success(openai_service, mock_openai_client):
    # Mock response data
    mock_embedding = [0.1, 0.2, 0.3]  # Simplified embedding vector
    mock_response = Mock()
    mock_response.data = [Mock(embedding=mock_embedding)]
    mock_response.model = "text-embedding-ada-002-v2"  # Example model version
    mock_response.usage = Mock(
        prompt_tokens=10,
        total_tokens=10
    )
    
    # Configure mock client
    mock_openai_client.embeddings.create.return_value = mock_response
    
    # Test input
    test_text = "Test text"
    
    # Call the service
    result = openai_service.create_embedding(test_text)
    
    # Verify the result
    assert isinstance(result, EmbeddingResponse)
    assert result.embedding == mock_embedding
    assert result.model == "text-embedding-ada-002-v2"
    assert result.usage == {
        "prompt_tokens": 10,
        "total_tokens": 10
    }
    
    # Verify the API was called correctly
    mock_openai_client.embeddings.create.assert_called_once_with(
        model=OpenAIService.DEFAULT_MODEL,
        input=test_text
    )

def test_create_embedding_empty_text(openai_service):
    with pytest.raises(OpenAIServiceError, match="Input text cannot be empty"):
        openai_service.create_embedding("")

def test_create_embedding_api_error(openai_service, mock_openai_client):
    from openai import APIError
    
    # Configure mock to raise an error with required arguments
    mock_openai_client.embeddings.create.side_effect = APIError(
        message="API Error",
        request=Mock(),
        body={"error": {"message": "API Error", "type": "api_error"}}
    )
    
    with pytest.raises(OpenAIServiceError, match="OpenAI API error: API Error"):
        openai_service.create_embedding("Test text")

def test_create_embedding_unexpected_error(openai_service, mock_openai_client):
    # Configure mock to raise an unexpected error
    mock_openai_client.embeddings.create.side_effect = Exception("Unexpected error")
    
    with pytest.raises(OpenAIServiceError, match="Unexpected error during embedding creation: Unexpected error"):
        openai_service.create_embedding("Test text") 