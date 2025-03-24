import os
import pytest

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ['OPENAI_API_KEY'] = 'test-openai-key'
    os.environ['PINECONE_API_KEY'] = 'test-pinecone-key'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    yield
    
    # Clean up environment variables after tests
    os.environ.pop('OPENAI_API_KEY', None)
    os.environ.pop('PINECONE_API_KEY', None)
    os.environ.pop('LOG_LEVEL', None) 