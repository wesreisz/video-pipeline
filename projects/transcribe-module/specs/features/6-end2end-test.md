# End-to-End Test: Creating and Transcribing an Audio File

This document outlines the process for conducting an end-to-end test of the AWS Transcribe module, from audio file creation to verifying the transcription output.

## Prerequisites

- Access to AWS resources (properly configured AWS CLI)
- S3 buckets created (dev-audio-transcribe-input and dev-audio-transcribe-output)
- Lambda function deployed (dev_audio_transcribe)
- Python environment set up with required dependencies
- Follow best practices for python on creating the folder structure for the end to end test

## Test Process

### 1. Create Test Audio File with Speech Content

Create a test audio file with clear speech content that can be reliably transcribed. You can use one of these approaches:

#### Option A: Download Sample Audio

```bash
# Download a sample audio file with speech content
curl -s -o speech-sample.mp3 https://filesamples.com/samples/audio/mp3/sample3.mp3
```

#### Option B: Create Using Text-to-Speech Service

```bash
# If available, use a text-to-speech service 
# Example using AWS Polly (if available):
aws polly synthesize-speech \
  --output-format mp3 \
  --voice-id Joanna \
  --text "This is a test of the audio transcription service. We are testing the end to end workflow from audio creation to transcription output." \
  speech-sample.mp3
```

### 2. Verify Audio File

Check that the audio file exists and has proper content:

```bash
# Verify the file size 
ls -la speech-sample.mp3

# Optional: Play the audio to confirm it has speech
# (For Mac/Linux environments)
afplay speech-sample.mp3  # Mac
# or
# play speech-sample.mp3  # Linux with SoX installed
```

### 3. Upload to Input Bucket

Upload the audio file to the input bucket to trigger the transcription process:

```bash
# Upload to the input bucket
aws s3 cp speech-sample.mp3 s3://dev-audio-transcribe-input/
```

### 4. Monitor Processing

Monitor the Lambda function's processing:

```bash
# Get the Lambda's most recent log stream
LOG_STREAM=$(aws logs describe-log-streams \
  --log-group-name /aws/lambda/dev_audio_transcribe \
  --order-by LastEventTime \
  --descending \
  --limit 1 \
  --query 'logStreams[0].logStreamName' \
  --output text)

# Tail the logs
aws logs get-log-events \
  --log-group-name /aws/lambda/dev_audio_transcribe \
  --log-stream-name $LOG_STREAM \
  --limit 20
```

### 5. Verify Transcription Output

Check for the transcription output in the output bucket:

```bash
# Wait for processing to complete (may take 15-30 seconds)
echo "Waiting for transcription to complete..."
sleep 30

# List objects in the output bucket
aws s3 ls s3://dev-audio-transcribe-output/transcriptions/ --recursive

# Get the transcription content
aws s3 cp s3://dev-audio-transcribe-output/transcriptions/speech-sample.json - | cat
```

### 6. Validate Results

Verify that:
1. The Lambda function processed the file successfully (check logs)
2. A transcription file was created in the output bucket
3. The transcription text matches what was spoken in the audio file

## Troubleshooting

If the test fails, check:

1. **Lambda execution**: Review CloudWatch logs for errors
2. **AWS Transcribe job**: Check AWS Transcribe console for the job status
3. **Audio format**: Ensure the audio file is in a format supported by AWS Transcribe
4. **Permissions**: Verify that the Lambda has the necessary permissions
5. **Network**: Ensure Lambda can access AWS Transcribe and S3 services

## Expected Output

A successful test should produce a transcription JSON file containing:
- Original file reference
- Timestamp
- Job ID reference
- Transcription text that matches the audio content

Example:
```json
{
  "original_file": "speech-sample.mp3",
  "transcription_text": "This is a test of the audio transcription service. We are testing the end to end workflow from audio creation to transcription output.",
  "timestamp": "2025-03-13T20:12:34.123456",
  "job_name": "transcribe-abcd1234-5678-efgh-9012-ijklmnopqrst"
}
```

## Clean Up

Remove test files after completion:

```bash
# Delete files from S3
aws s3 rm s3://dev-audio-transcribe-input/speech-sample.mp3
aws s3 rm s3://dev-audio-transcribe-output/transcriptions/speech-sample.json

# Remove local files
rm speech-sample.mp3
```
