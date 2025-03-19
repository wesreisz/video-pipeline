"""
Pytest configuration file for the chunking module tests.

This file defines common fixtures and command-line options for all pytest tests.
"""

import pytest

def pytest_addoption(parser):
    """Add command-line options for the tests."""
    parser.addoption(
        "--bucket", action="store", default=None, 
        help="S3 bucket containing the test file"
    )
    parser.addoption(
        "--key", action="store", default=None, 
        help="S3 key of the test file"
    )
    
@pytest.fixture(scope="session")
def s3_bucket(request):
    """Get the S3 bucket name from command line args."""
    return request.config.getoption("--bucket")

@pytest.fixture(scope="session")
def s3_key(request):
    """Get the S3 key from command line args."""
    return request.config.getoption("--key") 