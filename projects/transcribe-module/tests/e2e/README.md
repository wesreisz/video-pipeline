# End-to-End Testing for AWS Transcribe Module

This directory contains scripts for automated end-to-end testing of the AWS Transcribe module.

## Overview

The end-to-end test automates the following steps:

1. Creating a test audio file with speech content
2. Verifying the audio file
3. Uploading the audio file to the input S3 bucket
4. Monitoring the Lambda function processing
5. Verifying the transcription output
6. Cleaning up test resources

## Requirements

- Python 3.6+
- AWS CLI configured with appropriate credentials
- Deployed AWS Transcribe module (Lambda, S3 buckets)
- Internet access for downloading sample audio or using AWS Polly

## Running the Test

### Using the Shell Script (Recommended)

```bash
# Run with default settings
./run_test.sh

# Run with custom settings
./run_test.sh --input-bucket my-custom-input-bucket --output-bucket my-custom-output-bucket
```

### Running the Python Script Directly

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install boto3 requests

# Run the test
python test_transcribe_e2e.py

# Run with custom settings
python test_transcribe_e2e.py --input-bucket my-custom-input-bucket --output-bucket my-custom-output-bucket --region us-west-2
```

## Command-Line Arguments

The test script accepts the following command-line arguments:

- `--input-bucket`: S3 bucket for input audio files (default: `dev-audio-transcribe-input`)
- `--output-bucket`: S3 bucket for transcription output (default: `dev-audio-transcribe-output`)
- `--region`: AWS region to use (default: `us-east-1`)
- `--lambda-name`: Name of the Lambda function (default: `dev_audio_transcribe`)

## Output

The test script produces detailed logs of its operation, both in the console and in a timestamped log file in the current directory.

## Integration with CI/CD

The script can be easily integrated into CI/CD pipelines. It returns an exit code of 0 for successful tests and non-zero for failed tests.

Example integration with GitHub Actions:

```yaml
jobs:
  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Run End-to-End Test
        run: |
          cd projects/transcribe-module/tests/e2e
          chmod +x run_test.sh
          ./run_test.sh
``` 