# Testing Guide

This directory contains both unit tests and integration tests for the embedding module. Below are instructions on how to run these tests.

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

- OpenAI API key
- Python 3.11 or later
- pytest

#### Running Integration Tests

1. From the `embedding-module` directory, use the setup script:

```bash
# Format
./tests/scripts/setup_test_env.sh <your-openai-api-key> [test_file]

# Example: Run all integration tests
./tests/scripts/setup_test_env.sh "your-openai-api-key" "tests/integration/test_openai_service_integration.py"
```

The setup script will:
- Set the OpenAI API key
- Configure the organization ID
- Set up test AWS credentials
- Enable environment variable fallback
- Set appropriate log levels
- Run the specified tests

#### Environment Variables Set by the Script

| Variable | Description | Default Value |
|----------|-------------|---------------|
| ENVIRONMENT | Environment name | dev |
| RUN_LIVE_TESTS | Enable live API calls | 1 |
| LOG_LEVEL | Logging verbosity | INFO |
| USE_ENV_FALLBACK | Use environment variables when AWS Secrets unavailable | true |
| OPENAI_ORG_ID | OpenAI Organization ID | org-b6y2SlhOMQnynny57KMpe8Bk |
| AWS_ACCESS_KEY_ID | AWS access key for local testing | test |
| AWS_SECRET_ACCESS_KEY | AWS secret key for local testing | test |
| AWS_DEFAULT_REGION | AWS region for local testing | us-east-1 |

## Test Categories

### Unit Tests
- Located in `tests/services/`
- Test individual components in isolation
- Do not require API keys or external services
- Fast execution

### Integration Tests
- Located in `tests/integration/`
- Test interaction with external services (OpenAI API)
- Require valid API credentials
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
1. OpenAI API key is valid
2. Organization ID is correct
3. Network connectivity
4. Python environment has all required packages
5. You're in the correct directory (embedding-module)

For any issues, check the test output and logs for detailed error messages. 