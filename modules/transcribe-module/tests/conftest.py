import os
import sys
import pytest

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

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
        
        # Set environment variables specific to transcribe module
        os.environ['ENVIRONMENT'] = 'test'
        os.environ['TRANSCRIPTION_OUTPUT_BUCKET'] = 'test-transcription-bucket'
        os.environ['TRANSCRIBE_REGION'] = 'us-east-1'
        
    yield
    
    # Clean up environment variables after tests
    if not os.getenv('RUN_LIVE_TESTS'):
        for key in ['AWS_DEFAULT_REGION', 'AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 
                   'ENVIRONMENT', 'TRANSCRIPTION_OUTPUT_BUCKET', 'TRANSCRIBE_REGION']:
            os.environ.pop(key, None)

@pytest.fixture
def lambda_context():
    """Fixture for mock Lambda context."""
    class MockContext:
        def __init__(self):
            self.function_name = "test-transcribe-func"
            self.memory_limit_in_mb = 256
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789:function:test-transcribe-func"
            self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return MockContext() 