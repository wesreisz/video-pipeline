# Chunking Module Tests

This directory contains tests for the chunking module, which include both traditional unit tests and integration tests.

## Test Types

1. **Unit Tests**: These tests mock external dependencies and focus on testing individual components in isolation.
   - `test_chunking_handler.py` - Tests for the Lambda handler.

2. **Integration Tests**: These tests interact with real AWS services (S3) and test the full functionality.
   - Original scripts: `test_chunking.py` and `test_s3_utils.py` 
   - New pytest scripts: `pytest_chunking.py` and `pytest_s3_utils.py`

## Running the Tests

### Unit Tests

To run the unit tests:

```bash
# Navigate to the chunking-module directory
cd modules/chunking-module

# Create and activate a virtual environment (if not already done)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r dev-requirements.txt

# Run the pytest unit tests
PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m pytest -xvs tests/test_chunking_handler.py
```

### Integration Tests

#### Original Script Format

The original integration test scripts are designed to be run directly with command-line arguments:

```bash
# For test_chunking.py
PYTHONPATH=$PYTHONPATH:$(pwd)/src python tests/test_chunking.py --bucket YOUR_S3_BUCKET --key YOUR_S3_KEY

# For test_s3_utils.py
PYTHONPATH=$PYTHONPATH:$(pwd)/src python tests/test_s3_utils.py --bucket YOUR_S3_BUCKET --key YOUR_S3_KEY
```

#### New Pytest Format

The new pytest format allows running the integration tests using the standard pytest command:

```bash
# Run all integration tests
PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m pytest -xvs tests/pytest_chunking.py tests/pytest_s3_utils.py --bucket YOUR_S3_BUCKET --key YOUR_S3_KEY

# Run a specific test file
PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m pytest -xvs tests/pytest_chunking.py --bucket YOUR_S3_BUCKET --key YOUR_S3_KEY

# Run individual test functions using the -k option
PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m pytest -xvs tests/pytest_chunking.py::test_chunking_service --bucket YOUR_S3_BUCKET --key YOUR_S3_KEY
```

## Marking Tests

The integration tests are marked with `@pytest.mark.integration`. You can run only these marked tests:

```bash
PYTHONPATH=$PYTHONPATH:$(pwd)/src python -m pytest -xvs -m integration --bucket YOUR_S3_BUCKET --key YOUR_S3_KEY
```

## AWS Credentials

To run the integration tests, you need to have AWS credentials configured:

1. Configure AWS CLI with `aws configure`
2. Set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=your_region
   ```
3. Use an IAM role if running in an AWS environment

## Sample Input Files

You can use the following sample files for testing:
- Sample audio files in the `samples/` directory
- Transcription outputs in your S3 bucket 