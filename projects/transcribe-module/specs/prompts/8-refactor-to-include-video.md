# Refactor Transcribe Module to Support Video Files

## Overview

Extend the current audio transcription module to support video files in addition to audio files. This requires refactoring the code to properly detect file types, process both audio and video formats, and update the infrastructure accordingly.

## Requirements

1. The transcription module should accept and process both audio and video files.
2. Update all code, tests, and infrastructure to reflect this capability.
3. Maintain backward compatibility with existing audio processing.
4. Ensure the transcription results indicate whether the source was audio or video.

## Implementation Guidelines

### Code Changes

1. **TranscriptionService Class**:
   - Rename `process_audio` to `process_media` with enhanced media type detection
   - Maintain a backward-compatible `process_audio` method that calls `process_media`
   - Add logic to detect file type (audio vs. video) based on file extension:
     - Audio formats: mp3, wav, flac, ogg, amr
     - Video formats: mp4, webm
   - Pass media type information to the transcription result

2. **TranscriptionResult Model**:
   - Add a `media_type` field (values: 'audio' or 'video')
   - Default to 'audio' for backward compatibility
   - Include `media_type` in the serialized output

3. **Handler Updates**:
   - Update to use the new `process_media` method
   - Update documentation to reflect handling of both audio and video files

### Tests

1. Update existing tests to verify audio file handling still works
2. Add new tests for video file processing:
   - Unit tests for video extension detection
   - Integration tests with sample video files
   - Tests for the `media_type` field in results

### Infrastructure Changes

1. **S3 Buckets**:
   - Rename buckets from audio-specific to media-specific names
   - Example: `dev-audio-transcribe-input` → `dev-media-transcribe-input`

2. **Lambda Function**:
   - Update function name to reflect broader media handling
   - Example: `dev_audio_transcribe` → `dev_media_transcribe`

3. **S3 Event Notifications**:
   - Add triggers for video file formats (.mp4, .webm)
   - Maintain existing triggers for audio formats (.mp3, .wav)

### Documentation

1. Update README to reflect video support:
   - List supported audio and video formats
   - Update usage examples to include video files
   - Add troubleshooting info for video-specific issues

## Testing Procedure

1. Deploy the updated infrastructure
2. Upload a sample video file to the media input bucket
3. Verify that the Lambda function is triggered
4. Check the output bucket for the transcription result
5. Verify that the `media_type` field is correctly set to "video"

## Example

Refer to this implementation:
https://github.com/wesreisz/video-pipeline-experiment/blob/main/src/s3_event_processor/lambda_function.py

## Expected Outcome

A fully functional transcription service that can process both audio and video files, maintaining backward compatibility while providing clear indication of media type in results.