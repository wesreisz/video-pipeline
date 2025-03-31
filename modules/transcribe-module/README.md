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
   - Processes both word-level segments and sentence-level audio segments
   - Uploads the transcription result to the output bucket as JSON

## Getting Started

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 0.14
- Python 3.9+
- Docker (for local testing with LocalStack)
- AWS Transcribe service access

### Deployment

#### Option 1: Using the Automated Deployment Script (Recommended)

The project includes an automated deployment script that handles all the steps required to build, test, and deploy the module to the dev environment:

```bash
# Navigate to the dev environment directory
cd infra/environments/dev

# Run the deployment script
./deploy.sh
```

The script will:
1. Set up the necessary Python environment
2. Run tests to validate the code
3. Build the Lambda deployment package
4. Deploy the infrastructure using Terraform
5. Run an end-to-end test to verify the deployment was successful

#### Option 2: Manual Deployment

If you prefer to deploy manually, follow these steps:

1. Set up the module-specific virtual environment:
   ```
   cd modules/transcribe-module
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   # For production/runtime dependencies only
   pip install -r requirements.txt
   
   # For development, testing, and code quality tools
   pip install -r dev-requirements.txt
   ```

3. Run tests to validate the code:
   ```
   python -m pytest -xvs tests/
   ```

4. Build the Lambda deployment package:
   ```
   mkdir -p ../../infra/build
   cd ../..
   zip -r infra/build/transcribe_lambda.zip modules/transcribe-module/src/
   ```

5. Deploy to the dev environment:
   ```
   cd infra/environments/dev
   terraform init
   terraform plan -out=tfplan
   terraform apply "tfplan"
   ```

6. Validate the deployment using the end-to-end test:
   ```
   cd ../../../tests/e2e
   ./run_e2e_test.sh --cleanup
   ```

### Usage

Once deployed, you can use the module by:

1. Uploading a media file to the input S3 bucket:
   
   For audio files with metadata:
   ```bash
   aws s3 cp ./sample.mp3 s3://dev-media-transcribe-input/audio/sample.mp3 \
     --metadata '{"speaker":"John Doe","title":"Sample Talk","track":"Technical Track","day":"Monday"}' \
     --metadata-directive REPLACE
   ```
   
   For video files with metadata:
   ```bash
   aws s3 cp ./sample.mp4 s3://dev-media-transcribe-input/media/sample.mp4 \
     --metadata '{"speaker":"Jane Smith","title":"Video Presentation","track":"Main Track","day":"Tuesday"}' \
     --metadata-directive REPLACE
   ```

   Supported metadata fields:
   - `speaker`: Name of the speaker(s) in the recording
   - `title`: Title of the talk or presentation
   - `track`: Track or category of the talk
   - `day`: Day of the week the talk was given

   Note: All metadata fields are optional. The pipeline will continue processing even if metadata is not provided.

2. The transcription will automatically be generated and stored in the output bucket:
   ```bash
   aws s3 ls s3://dev-media-transcribe-output/transcriptions/
   ```

   The transcription process will:
   - Log the metadata information during processing
   - Include the metadata in the EventBridge response
   - Continue processing even when metadata is not present

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

### Unit and Integration Tests

Run tests using pytest (recommended):
```bash
cd modules/transcribe-module
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
# Run tests with pytest
python -m pytest -xvs tests/
```

Alternative: Run tests using unittest:
```bash
cd modules/transcribe-module
python -m unittest discover tests
```

Or use the Makefile from the project root:
```bash
make unit-tests
```

### End-to-End Tests

End-to-end tests have been consolidated at the project level. To validate the full pipeline after deployment:

```bash
cd ../../../tests/e2e
./run_e2e_test.sh --cleanup
```

This consolidated test script will:
1. Upload a sample audio file to the input bucket
2. Wait for the transcription to complete
3. Verify the transcription results
4. Validate the chunking process
5. Clean up test files (if --cleanup flag is provided)

For more details, see the project-level README and the documentation in the `tests/e2e` directory.

### Local Integration Testing

This project includes several options for local testing:

#### Option 1: Using the provided helper script

1. Start LocalStack in the background:
   ```bash
   make start-localstack
   ```

2. Run the local test script:
   ```bash
   make test-local
   ```

3. When done, stop LocalStack:
   ```bash
   make stop-localstack
   ```

#### Option 2: Using Docker Compose

1. Start all services:
   ```bash
   docker-compose up -d
   ```

2. Run the test script:
   ```bash
   python modules/transcribe-module/local_test.py
   ```

3. Browse S3 content at http://localhost:8000

4. Stop all services:
   ```bash
   docker-compose down
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
- **Deployment issues**: If you encounter issues during deployment, check the logs from the deploy.sh script. You can also try the manual deployment steps to isolate the problem.

## Contributing

Follow the project's code style and ensure that tests pass before submitting pull requests. Always use the deploy.sh script to verify your changes work in the dev environment.

## Transcription Result Format

The transcription results are stored as JSON files in the output S3 bucket with the following structure:

```json
{
  "original_file": "path/to/original.mp3",
  "transcription_text": "Full transcription text",
  "timestamp": "2023-04-01T12:00:00",
  "job_name": "transcribe-abc123",
  "media_type": "audio",
  "metadata": {
    "speaker": "John Doe",
    "title": "Sample Talk",
    "track": "Technical Track",
    "day": "Monday"
  },
  "segments": [
    {
      "type": "pronunciation",
      "content": "Word",
      "start_time": "0.0",
      "end_time": "0.5",
      "confidence": "0.98"
    },
    // More word-level segments
  ],
  "audio_segments": [
    {
      "id": 0,
      "transcript": "Complete sentence text.",
      "start_time": "0.0",
      "end_time": "2.5",
      "items": [0, 1, 2, 3, 4]
    },
    // More sentence-level segments
  ]
}
```

### Field Descriptions

- `original_file`: Path to the original audio or video file
- `transcription_text`: The complete transcribed text
- `timestamp`: ISO-formatted timestamp of when the transcription was created
- `job_name`: AWS Transcribe job name
- `media_type`: Type of media ('audio' or 'video')
- `metadata`: Object containing file metadata (if provided during upload):
  - `speaker`: Name of the speaker(s)
  - `title`: Title of the talk
  - `track`: Track or category
  - `day`: Day of the week
- `segments`: List of time-stamped word-level segments from the transcription
- `audio_segments`: List of sentence-level audio segments, each containing:
  - `id`: Sentence identifier
  - `transcript`: The complete sentence text
  - `start_time`: Start time of the sentence in seconds
  - `end_time`: End time of the sentence in seconds
  - `items`: References to the word-level segment IDs that make up this sentence

For more detailed information on the sentence-level audio segments feature, see the [documentation](docs/sentence-level-segments.md).
