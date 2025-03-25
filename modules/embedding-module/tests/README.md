# Embedding Module Tests

This directory contains tests for the embedding module, including unit tests and integration tests with the OpenAI API.

## Test Structure

```
tests/
├── unit/               # Unit tests
│   └── test_embedding_handler.py
├── integration/        # Integration tests
│   └── test_openai_service.py
├── scripts/           # Test utility scripts
│   └── setup_test_env.sh
├── conftest.py        # Shared test fixtures
└── README.md          # This file
```

## Running Tests

### Unit Tests

To run unit tests for specific components:

```bash
# Run embedding handler tests
python -m pytest tests/unit/test_embedding_handler.py -vv

# Run all unit tests
python -m pytest tests/unit -vv
```

### Integration Tests

To run integration tests that use mocked external services:

```bash
# Run OpenAI service tests
python -m pytest tests/integration/test_openai_service.py -vv

# Run all integration tests
python -m pytest tests/integration -vv
```

### Live API Tests

To run tests that make actual API calls to OpenAI:

1. Set up your environment using the provided script:
   ```bash
   # From the embedding-module directory
   source tests/scripts/setup_test_env.sh <your-openai-api-key>
   ```

2. Run the tests with live API enabled:
   ```bash
   # Set environment variable to enable live tests
   export RUN_LIVE_TESTS=1

   # Run OpenAI service tests including live API tests
   python -m pytest tests/integration/test_openai_service.py -vv
   ```

### Running All Tests

To run all tests (excluding live API tests):

```bash
python -m pytest -vv
```

Common pytest options:
- `-vv`: Very verbose output
- `-s`: Show print statements during test execution
- `-k "test_name"`: Run tests matching the given name
- `--pdb`: Drop into debugger on test failures

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for live tests)
- `RUN_LIVE_TESTS`: Set to 1 to enable live API tests
- `OPENAI_BASE_URL`: Optional custom API endpoint
- `OPENAI_ORG_ID`: Optional organization ID

## Adding New Tests

1. Follow the naming conventions:
   - Test files: `test_*.py`
   - Test functions: `test_*`
   - Test classes: `Test*`

2. Use appropriate markers:
   - `@pytest.mark.integration` for integration tests
   - Add new markers in `pytest.ini` if needed

3. Add fixtures to `conftest.py` if they're shared across multiple tests

## Best Practices

1. Keep tests independent and idempotent
2. Use fixtures for setup and teardown
3. Mock external services when possible
4. Use descriptive test names
5. Include both positive and negative test cases

## Test Categories

- **Unit Tests**: Tests for individual components in isolation
  - Located in `tests/unit/`
  - No external service dependencies
  - Fast execution

- **Integration Tests**: Tests that verify integration with external services (OpenAI API)
  - Located in `tests/integration/`
  - Marked with `@pytest.mark.integration`
  - Some require API keys and are skipped by default 