# Media Transcription Module

This module is part of the video pipeline project and handles transcription of audio and video files using AWS Lambda and S3.

## Overview

The transcription module works as follows:

1. Media files (audio: .mp3, .wav, .flac, .ogg | video: .mp4, .webm) are uploaded to an S3 input bucket
2. An S3 event triggers the Lambda function
3. The Lambda function:
   - Starts an AWS Transcribe job for the media file
   - Waits for the transcription job to complete
   - Extracts the transcription text from the AWS Transcribe output
   - Uploads the transcription result to the output bucket as JSON

## Getting Started

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 0.14
- Python 3.9+
- Docker (for local testing with LocalStack)
- AWS Transcribe service access

### Deployment

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Deploy to the dev environment:
   ```
   cd infra/environments/dev
   terraform init
   terraform apply
   ```

### Usage

Once deployed, you can use the module by:

1. Uploading a media file to the input S3 bucket:
   
   For audio files:
   ```
   aws s3 cp samples/sample.mp3 s3://dev-media-transcribe-input/audio/
   ```
   
   For video files:
   ```
   aws s3 cp samples/sample.mp4 s3://dev-media-transcribe-input/media/
   ```

2. The transcription will automatically be generated and stored in the output bucket:
   ```
   aws s3 ls s3://dev-media-transcribe-output/transcriptions/
   ```

## Supported Media Formats

This module supports transcription of the following media types:

### Audio Formats
- MP3 (.mp3)
- WAV (.wav, .wave)
- FLAC (.flac)
- OGG (.ogg)
- AMR (.amr)

### Video Formats
- MP4 (.mp4)
- WebM (.webm)

## Project Structure

- `src/`: Lambda function code
  - `handlers/`: Lambda entry points
  - `services/`: Business logic for transcription
  - `models/`: Data structures
  - `utils/`: Helper functions and utilities
- `tests/`: Unit tests
- `specs/`: Design documents and specifications

## Testing

### Unit Tests

Run unit tests:
```
cd projects/transcribe-module
python -m unittest discover tests
```

Or use the Makefile from the project root:
```
make unit-tests
```

### Local Integration Testing

This project includes several options for local testing:

#### Option 1: Using the provided helper script

1. Start LocalStack in the background:
   ```
   make start-localstack
   ```

2. Run the local test script:
   ```
   make test-local
   ```

3. When done, stop LocalStack:
   ```
   make stop-localstack
   ```

#### Option 2: Using Docker Compose

1. Start all services:
   ```
   docker-compose up -d
   ```

2. Run the test script:
   ```
   python projects/transcribe-module/local_test.py
   ```

3. Browse S3 content at http://localhost:8000

4. Stop all services:
   ```
   docker-compose down
   ```

#### Option 3: AWS SAM CLI

For more advanced local Lambda testing with AWS SAM:

1. Install AWS SAM CLI
2. Create a template.yaml file in the project root
3. Run:
   ```
   sam local invoke -e events/s3-event.json
   ```

## Environment Variables

The Lambda function uses the following environment variables:

- `TRANSCRIPTION_OUTPUT_BUCKET`: The S3 bucket where transcription results are stored
- `TRANSCRIBE_REGION`: The AWS region for the Transcribe service (defaults to us-east-1)

## Troubleshooting

- **Error connecting to LocalStack**: Make sure Docker is running and the LocalStack container is accessible.
- **Missing AWS credentials**: For local testing, LocalStack uses dummy credentials (access_key=test, secret_key=test).
- **Lambda timeout**: Increase the timeout value in the Terraform configuration.
- **Transcribe job failures**: Check the CloudWatch logs for the Lambda function and the Transcribe service console.
- **Unsupported media format**: Check that your file format is in the list of supported formats above.

## Contributing

Follow the project's code style and ensure that tests pass before submitting pull requests.