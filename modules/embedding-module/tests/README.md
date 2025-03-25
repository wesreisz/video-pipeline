# Embedding Module Tests

This directory contains tests for the embedding module, including unit tests and integration tests with the OpenAI API.

## Test Structure

```
tests/
├── integration/          # Integration tests
│   └── test_openai_service.py
├── scripts/             # Test utility scripts
│   └── setup_test_env.sh
├── conftest.py          # Shared test fixtures
└── README.md           # This file
```

## Running Tests

### Regular Tests (No API Calls)

To run all tests except those requiring API access:

```bash
pytest -v
```

### Live API Tests

To run tests that make actual API calls to OpenAI:

1. Set up your environment:
   ```bash
   source tests/scripts/setup_test_env.sh <your-openai-api-key>
   ```

2. Run the tests:
   ```bash
   # Run all tests including live API tests
   pytest -v
   
   # Run only integration tests
   pytest tests/integration -v
   
   # Run a specific test file
   pytest tests/integration/test_openai_service.py -v
   ```

### Test Categories

- **Integration Tests**: Tests that verify integration with external services (OpenAI API)
  - Located in `tests/integration/`
  - Marked with `@pytest.mark.integration`
  - Some require API keys and are skipped by default

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for live tests)
- `RUN_LIVE_TESTS`: Set to 1 to enable live API tests

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