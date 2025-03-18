# End-to-End Testing for Video Transcription Pipeline

This directory contains tools for end-to-end testing of the video transcription pipeline. These tests verify that the complete pipeline functions correctly after deployment.

## Overview

The testing solution consists of:

1. A Python script (`test_pipeline_e2e.py`) that verifies the pipeline functionality by:
   - Uploading a sample audio/video file to the input bucket
   - Waiting for processing to complete
   - Verifying the transcription output
   - Providing clear success/failure feedback

2. A shell script wrapper (`run_e2e_test.sh`) that:
   - Sets up a Python virtual environment
   - Installs required dependencies from project's requirements.txt
   - Automatically extracts bucket names from Terraform outputs
   - Runs the Python test with appropriate parameters
   - Handles errors gracefully
   - Provides clear, formatted output

## Prerequisites

Before running the tests, you need:

1. **Python 3**: The test requires Python 3.6 or later.

2. **AWS CLI Configuration**: AWS credentials must be configured either via environment variables or the AWS CLI configuration.

3. **Terraform State**: The testing environment must be deployed using Terraform, and the Terraform state must be accessible.

4. **Sample Media Files**: You need a sample audio/video file for testing. By default, the test uses the `hello-my_name_is_wes.mp3` file from the `samples` directory.

## Virtual Environment and Dependencies

The test script automatically:

1. Creates a Python virtual environment in the `.venv` directory (if it doesn't exist)
2. Activates the virtual environment
3. Installs dependencies from the module's `dev-requirements.txt` file
4. Uses the virtual environment's Python interpreter to run the test

The main dependencies include:
- boto3: AWS SDK for Python
- pytest: Testing framework

## Usage

### Basic Usage

The simplest way to run the test is to navigate to the e2e test directory and run the shell script without arguments:

```bash
cd modules/transcribe-module/tests/e2e
./run_e2e_test.sh
```

This will:
1. Set up the virtual environment and install dependencies
2. Use the default sample file and timeout values
3. Run the test against your deployed infrastructure

### Advanced Usage

You can customize the test execution with the following options:

```bash
./run_e2e_test.sh --file /path/to/sample.mp3 --timeout 600 --venv /path/to/custom/venv
```

Options:
- `-f, --file PATH`: Path to sample audio/video file (default: samples/hello-my_name_is_wes.mp3)
- `-t, --timeout SECONDS`: Timeout in seconds (default: 300)
- `-v, --venv DIR`: Custom virtual environment directory (default: ./venv)
- `--skip-venv`: Skip virtual environment setup (use system Python)
- `-h, --help`: Show help message

### Running the Python Script Directly

You can also run the Python script directly with your own parameters, but you need to ensure the required dependencies are installed:

```bash
# Ensure dependencies are installed
pip install -r ../../dev-requirements.txt

# Run the test
./test_pipeline_e2e.py \
  --input-bucket your-input-bucket-name \
  --output-bucket your-output-bucket-name \
  --sample-file /path/to/sample.mp3 \
  --timeout 300
```

## Test Flow

1. **Preparation**:
   - Virtual environment is set up and dependencies are installed
   - Bucket names are extracted from Terraform outputs
   - Prerequisites are verified (AWS credentials, Python dependencies)
   - A unique test ID is generated to prevent conflicts

2. **Execution**:
   - The sample file is uploaded to the input bucket
   - The test waits for the transcription to appear in the output bucket
   - The transcription content is downloaded and verified

3. **Verification**:
   - The test checks that the transcription contains valid data
   - Success or failure is reported with clear messaging
   - The exit code indicates test result (0 for success, 1 for failure)

## Integration with CI/CD

To integrate these tests with CI/CD pipelines:

1. Add the necessary AWS credentials and permissions to your CI/CD environment.

2. Make sure Python 3 is available in your CI/CD environment.

3. Run the tests as part of your deployment pipeline:
   ```bash
   cd modules/transcribe-module/tests/e2e
   ./run_e2e_test.sh --timeout 600
   ```

4. Use the exit code to determine if the deployment was successful:
   ```bash
   if [ $? -ne 0 ]; then
     echo "E2E tests failed, rolling back deployment"
     # Add rollback logic here
     exit 1
   fi
   ```

## Troubleshooting

### Common Issues and Solutions

1. **Virtual Environment Setup Issues**:
   - Ensure Python 3 is installed and available in your PATH
   - Try running with `--skip-venv` to use system Python
   - Check permissions on the directory where the virtual environment is created

2. **Dependency Installation Issues**:
   - Verify that the module's dev-requirements.txt file is accessible
   - Check your internet connection for package downloads
   - If behind a proxy, ensure proxy settings are configured

3. **Timeout Error**:
   - Increase the timeout value: `./run_e2e_test.sh --timeout 600`
   - Check the AWS Lambda logs for errors
   - Verify that the S3 trigger is properly configured

4. **AWS Credentials Error**:
   - Ensure AWS credentials are configured: `aws configure`
   - Check that the IAM role has sufficient permissions

5. **Terraform Output Error**:
   - Make sure you've applied the Terraform configuration: `terraform apply`
   - Check that you're in the correct environment directory

6. **Transcription Format Error**:
   - Verify that the sample file is in a supported format
   - Check the AWS Transcribe service logs for errors

### Getting Help

If you encounter issues not covered in this guide:

1. Check the AWS CloudWatch logs for the Lambda function
2. Review the Amazon Transcribe service documentation
3. Examine the S3 bucket permissions and policies
4. Contact the DevOps team for assistance 