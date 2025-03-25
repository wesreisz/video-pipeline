import os
import pytest
from unittest.mock import patch, MagicMock
from typing import List, Dict
import openai

from src.services.openai_service import OpenAIService, OpenAIServiceError, EmbeddingResponse

# Mock response data
MOCK_EMBEDDING = [0.1] * 1536  # OpenAI's ada-002 produces 1536-dimensional vectors
MOCK_RESPONSE = MagicMock(
    data=[
        MagicMock(
            embedding=MOCK_EMBEDDING,
        )
    ],
    usage=MagicMock(
        prompt_tokens=10,
        total_tokens=10
    )
)

@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    client = MagicMock()
    client.embeddings.create.return_value = MOCK_RESPONSE
    return client

@pytest.fixture
def openai_service(mock_openai_client):
    """Create an OpenAI service instance with mock client for testing."""
    return OpenAIService(client=mock_openai_client)

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv('RUN_LIVE_TESTS'), reason="Live API tests are disabled")
def test_live_api_embedding_creation():
    """
    Test creating embeddings using the live OpenAI API.
    This test is skipped by default and only runs when RUN_LIVE_TESTS is set.
    """
    # Create service without mock client to use real API
    service = OpenAIService()
    
    # Sample text for embedding
    test_text = "This is a test sentence for embedding creation."
    
    # Create embedding
    response = service.create_embedding(test_text)
    
    # Verify response structure
    assert isinstance(response, EmbeddingResponse)
    assert isinstance(response.embedding, list)
    assert len(response.embedding) == 1536  # ada-002 model produces 1536-dimensional vectors
    assert all(isinstance(x, float) for x in response.embedding)
    assert response.model == "text-embedding-ada-002"
    assert isinstance(response.usage, dict)
    assert "prompt_tokens" in response.usage
    assert "total_tokens" in response.usage

@pytest.mark.integration
def test_mocked_embedding_creation(openai_service, mock_openai_client):
    """Test creating embeddings using a mocked OpenAI API."""
    # Test embedding creation
    test_text = "This is a test sentence for embedding creation."
    response = openai_service.create_embedding(test_text)
    
    # Verify the mock was called correctly
    mock_openai_client.embeddings.create.assert_called_once_with(
        model="text-embedding-ada-002",
        input=test_text
    )
    
    # Verify response
    assert isinstance(response, EmbeddingResponse)
    assert response.embedding == MOCK_EMBEDDING
    assert response.model == "text-embedding-ada-002"
    assert response.usage == {
        "prompt_tokens": 10,
        "total_tokens": 10
    }

@pytest.mark.integration
def test_empty_text_handling(openai_service):
    """Test handling of empty input text."""
    with pytest.raises(OpenAIServiceError, match="Input text cannot be empty"):
        openai_service.create_embedding("")

@pytest.mark.integration
def test_api_error_handling(mock_openai_client):
    """Test handling of API errors."""
    # Configure mock to raise an error
    error_message = "API request failed: rate limit exceeded"
    mock_openai_client.embeddings.create.side_effect = Exception(error_message)
    
    # Create service with error-raising mock
    service = OpenAIService(client=mock_openai_client)
    
    # Test error handling
    with pytest.raises(OpenAIServiceError, match=f"Unexpected error during embedding creation: {error_message}"):
        service.create_embedding("test text") 