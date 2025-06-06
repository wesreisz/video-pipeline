import os
import sys
import pytest

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Add any shared fixtures here if needed in the future

@pytest.fixture(autouse=True)
def setup_aws_environment():
    """Setup AWS environment variables for testing."""
    # Only set mock environment variables if we're not running live tests
    if not os.getenv('RUN_LIVE_TESTS'):
        # Set AWS region and dummy credentials for boto3
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['AWS_REGION'] = 'us-east-1'
        os.environ['AWS_ACCESS_KEY_ID'] = 'test-access-key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret-key'
        
        # Set other environment variables that might be needed
        os.environ['ENVIRONMENT'] = 'test'
        os.environ['USE_ENV_FALLBACK'] = 'true'
        
    yield
    
    # Clean up environment variables after tests
    if not os.getenv('RUN_LIVE_TESTS'):
        for key in ['AWS_DEFAULT_REGION', 'AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 
                   'ENVIRONMENT', 'USE_ENV_FALLBACK']:
            os.environ.pop(key, None)

@pytest.fixture
def lambda_context():
    """Fixture for mock Lambda context."""
    class MockContext:
        def __init__(self):
            self.function_name = "test-func"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:eu-west-1:809313241:function:test-func"
            self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return MockContext() 