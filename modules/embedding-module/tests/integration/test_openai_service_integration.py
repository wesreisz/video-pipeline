import os
import pytest
from services.openai_service import OpenAIService, OpenAIServiceError
from services.secrets_service import SecretsService

# Skip all tests in this module unless RUN_LIVE_TESTS is set
pytestmark = pytest.mark.skipif(
    not os.environ.get('RUN_LIVE_TESTS'),
    reason="Live tests are disabled. Set RUN_LIVE_TESTS=1 to enable."
)

@pytest.fixture
def openai_service():
    """Create a real OpenAI service instance."""
    return OpenAIService()

def test_create_embedding_live(openai_service):
    """Test creating an embedding using the real OpenAI API."""
    # Test with a simple, known text
    test_text = "This is a test of the OpenAI embedding API."
    
    response = openai_service.create_embedding(test_text)
    
    # Basic validation of the response
    assert len(response.embedding) > 0  # Should have embedding values
    assert response.model.startswith("text-embedding")  # Should use text embedding model
    assert response.usage["prompt_tokens"] > 0  # Should have used some tokens
    assert response.usage["total_tokens"] > 0  # Should have total token usage

def test_create_embedding_with_long_text(openai_service):
    """Test creating an embedding with a longer text."""
    # Create a longer text (about 100 words)
    test_text = " ".join(["test"] * 100)
    
    response = openai_service.create_embedding(test_text)
    
    # Validate response
    assert len(response.embedding) > 0
    assert response.usage["prompt_tokens"] > 50  # Should use more tokens for longer text

def test_create_embedding_with_special_chars(openai_service):
    """Test creating an embedding with special characters."""
    test_text = "Special characters: !@#$%^&*()_+ and emojis: 👋🌟🎉"
    
    response = openai_service.create_embedding(test_text)
    
    # Validate response
    assert len(response.embedding) > 0
    assert response.model.startswith("text-embedding") 