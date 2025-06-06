"""
Shared pytest fixtures for the embedding module tests.
"""
import os
import sys
import pytest

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '../src'))
sys.path.insert(0, src_dir)
print(f"Added path: {src_dir}")
print(f"Python path: {sys.path}")

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    # Only set mock environment variables if we're not running live tests
    if not os.getenv('RUN_LIVE_TESTS'):
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        os.environ['OPENAI_BASE_URL'] = 'https://test.openai.com/v1'
        os.environ['OPENAI_ORG_ID'] = 'test-org-id'
        # Add AWS region and credentials for boto3
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'test-access-key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret-key'
    yield
    # Clean up only the variables we might have set
    if not os.getenv('RUN_LIVE_TESTS'):
        for key in ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'OPENAI_ORG_ID', 
                   'AWS_DEFAULT_REGION', 'AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            os.environ.pop(key, None)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Only set test environment variables if we're not running live tests
    if not os.getenv('RUN_LIVE_TESTS'):
        os.environ['OPENAI_API_KEY'] = 'test-openai-key'
        # Add AWS environment variables if not already set
        if 'AWS_DEFAULT_REGION' not in os.environ:
            os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        if 'AWS_REGION' not in os.environ:
            os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    
    yield
    
    # Clean up environment variables after tests
    if not os.getenv('RUN_LIVE_TESTS'):
        os.environ.pop('OPENAI_API_KEY', None)
    os.environ.pop('LOG_LEVEL', None) 