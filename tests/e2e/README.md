# Consolidated End-to-End Testing for Video Pipeline

This directory contains tools for end-to-end testing of the complete video pipeline. These tests verify that the entire pipeline functions correctly after deployment, including both the transcription and chunking services.

## Overview

The end-to-end test performs the following steps:

1. Uploads a sample audio/video file to the input S3 bucket
2. Waits for the transcription service to process the file
3. Verifies the transcription output structure and content
4. Checks that the chunking service has processed the transcription
5. Displays sentence-level audio segments from the chunking service
6. Cleans up test files (optional)

## Components

The end-to-end test consists of:

1. A Python script (`pipeline_e2e_test.py`) that:
   - Uploads a sample audio/video file to the input S3 bucket
   - Waits for and validates the transcription output
   - Verifies the chunking service output
   - Displays sentence-level audio segments processed by the chunking service
   - Cleans up test files if requested

2. A shell script wrapper (`run_e2e_test.sh`) that:
   - Sets up the Python environment
   - Handles command-line arguments
   - Checks for AWS credentials
   - Runs the Python test script with appropriate parameters
   - Manages the virtual environment

## Prerequisites

Before running the tests, ensure that:

1. AWS CLI is installed and configured with appropriate credentials
2. Python 3.8+ is installed
3. Python dependencies are installed (boto3)
4. The pipeline infrastructure is deployed to AWS

## Running the Tests

The simplest way to run the test is to navigate to the e2e test directory and run the shell script without arguments:

```bash
cd tests/e2e
./run_e2e_test.sh
```

This will use the default configuration. You can customize the test run with various options:

```bash
# Run with cleanup of test files
./run_e2e_test.sh --cleanup

# Specify a different sample file
./run_e2e_test.sh --file /path/to/sample.mp3

# Specify input and output buckets
./run_e2e_test.sh --input-bucket my-input-bucket --output-bucket my-output-bucket

# Increase the timeout (for slow networks)
./run_e2e_test.sh --timeout 600

# Use a specific virtual environment
./run_e2e_test.sh --venv /path/to/venv
```

## Advanced Usage

You can run the Python script directly for more control:

```bash
cd tests/e2e
python pipeline_e2e_test.py \
  --input-bucket dev-media-transcribe-input \
  --output-bucket dev-media-transcribe-output \
  --sample-file ../../samples/sample.mp3 \
  --timeout 300 \
  --cleanup
```

## Troubleshooting

If the test fails, check:

1. AWS permissions - ensure your IAM user has sufficient permissions
2. S3 bucket configuration - check that the input and output buckets exist
3. Sample file - confirm the sample file is a valid audio/video file
4. Network connectivity - ensure your network can reach AWS services
5. Deployment state - verify that the pipeline infrastructure is deployed
6. Lambda function logs - check CloudWatch logs for any errors
7. Timeout - if the test times out, increase the timeout value with `--timeout 600`

## CI/CD Integration

You can integrate these end-to-end tests into your CI/CD pipeline by running:

```bash
cd tests/e2e
./run_e2e_test.sh --cleanup

if [ $? -ne 0 ]; then
  echo "E2E tests failed, rolling back deployment"
  # Add rollback commands here
  exit 1
fi
``` 