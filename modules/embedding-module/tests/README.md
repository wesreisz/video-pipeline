# Testing Guide

This directory contains both unit tests and integration tests for the embedding module. Below are instructions on how to run these tests.

## Virtual Environment Setup

Before running tests, set up and activate your virtual environment:

```bash
# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Install requirements
pip install -r requirements.txt
```

## Test Structure

```
tests/
├── integration/          # Integration tests
│   └── test_openai_service_integration.py
├── scripts/             # Test setup scripts
│   └── setup_test_env.sh
├── services/            # Unit tests
│   └── test_openai_service.py
└── README.md            # This file
```

## Running Tests

### Unit Tests

Unit tests can be run directly using pytest:

```bash
# Run all unit tests
python -m pytest tests/services/ -v

# Run a specific test file
python -m pytest tests/services/test_openai_service.py -v
```

### Integration Tests

Integration tests require proper environment setup, including API keys and configuration. We provide a setup script to help with this.

#### Prerequisites

For OpenAI tests:
- OpenAI API key
- OpenAI Organization ID (defaults to org-b6y2SlhOMQnynny57KMpe8Bk)
- Python 3.11 or later
- pytest
- `openai>=1.0.0` package (installed via requirements.txt)

Available OpenAI tests:
- `test_create_embedding_live`: Tests basic embedding creation
- `test_create_embedding_with_long_text`: Tests embedding creation with long text
- `test_create_embedding_with_special_chars`: Tests embedding creation with special characters

#### Running Integration Tests

1. From the `embedding-module` directory, use the setup script:

```bash
# Format
./tests/scripts/setup_test_env.sh <api-key> <test-file>

# Example: Run OpenAI integration tests (requires OpenAI API key)
./tests/scripts/setup_test_env.sh "your-openai-api-key" tests/integration/test_openai_service_integration.py
```

The setup script will:
- Set the appropriate API key based on the test file
- Configure the necessary environment (OpenAI org ID)
- Set up test AWS credentials
- Enable environment variable fallback
- Set appropriate log levels
- Run the specified tests

#### Environment Variables Set by the Script

| Variable | Description | Default Value | Required For |
|----------|-------------|---------------|--------------|
| ENVIRONMENT | Environment name | dev | All tests |
| RUN_LIVE_TESTS | Enable live API calls | 1 | All tests |
| LOG_LEVEL | Logging verbosity | INFO | All tests |
| USE_ENV_FALLBACK | Use environment variables when AWS Secrets unavailable | true | All tests |
| OPENAI_API_KEY | OpenAI API key | (provided) | OpenAI tests |
| OPENAI_ORG_ID | OpenAI Organization ID | org-b6y2SlhOMQnynny57KMpe8Bk | OpenAI tests |
| AWS_ACCESS_KEY_ID | AWS access key for local testing | test | All tests |
| AWS_SECRET_ACCESS_KEY | AWS secret key for local testing | test | All tests |
| AWS_DEFAULT_REGION | AWS region for local testing | us-east-1 | All tests |

## Test Categories

### Unit Tests
- Located in `tests/services/`
- Test individual components in isolation
- Do not require API keys or external services
- Fast execution

### Integration Tests
- Located in `tests/integration/`
- Test interaction with external services (OpenAI API)
- Require valid API credentials for the specific service being tested
- Test real API responses and error handling
- Slower execution due to network calls

## Adding New Tests

When adding new tests:
1. Unit tests go in `tests/services/`
2. Integration tests go in `tests/integration/`
3. Follow existing naming conventions
4. Add appropriate fixtures in `conftest.py` if needed
5. Update this README if adding new test categories or requirements

## Troubleshooting

If tests fail, check:
1. You're using the correct API key for the test you're running
2. The API key is valid
3. Service-specific configuration is correct:
   - For OpenAI: Organization ID
4. Network connectivity
5. Python environment has all required packages
6. You're in the correct directory (embedding-module)

## Common Issues

### OpenAI Tests
- Ensure your API key has sufficient credits
- Check organization ID if using a team account

For any issues, check the test output and logs for detailed error messages.

## Known Warnings

### Pytest-asyncio Warning
You may see a deprecation warning about `asyncio_default_fixture_loop_scope`. This warning doesn't affect test execution and will be resolved in future versions of pytest-asyncio. The warning looks like:
```
PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
``` 