# Sentence-Level Audio Segments Support

## Overview

This document describes the implementation of sentence-level audio segments support in the Transcription Module. AWS Transcribe provides multiple types of speech recognition data, including sentence-level audio segments which group words into logical sentences with timing information.

## Implementation Details

### TranscriptionResult Model

The `TranscriptionResult` model has been extended to include:

- A new `audio_segments` field in the constructor
- Updated serialization/deserialization methods to handle audio segments
- Backward compatibility with existing transcription data

```python
class TranscriptionResult:
    def __init__(self, original_file, transcription_text, timestamp, job_name=None, 
                 media_type='audio', segments=None, audio_segments=None):
        # ...
        self.audio_segments = audio_segments or []
        
    def to_dict(self):
        # ...
        if self.audio_segments:
            result['audio_segments'] = self.audio_segments
        # ...
        
    @classmethod
    def from_dict(cls, data):
        # ...
        audio_segments=data.get('audio_segments', [])
        # ...
```

### TranscriptionService Updates

The transcription service was updated to:

1. Extract sentence-level audio segments from AWS Transcribe results
2. Process these segments alongside the existing word-level segments
3. Include them in the final output

```python
# Extraction from AWS Transcribe response
audio_segments = results.get('audio_segments', [])

# Process sentence-level audio segments
processed_audio_segments = []
if audio_segments:
    logger.info(f"Extracted {len(audio_segments)} sentence-level segments")
    
    for segment in audio_segments:
        processed_audio_segment = {
            'id': segment.get('id'),
            'transcript': segment.get('transcript', ''),
            'start_time': segment.get('start_time'),
            'end_time': segment.get('end_time'),
            'items': segment.get('items', [])
        }
        processed_audio_segments.append(processed_audio_segment)
```

### Media Type Detection

We've also improved media type detection for different file extensions:

- Audio files: mp3, wav, flac, ogg, amr
- Video files: mp4, avi, mov, mkv, webm

## JSON Output Format

The JSON output from the transcription service now includes a new `audio_segments` field alongside the existing `segments` field:

```json
{
  "original_file": "example.mp3",
  "transcription_text": "This is an example transcription.",
  "timestamp": "2023-04-01T12:00:00",
  "media_type": "audio",
  "job_name": "transcribe-12345",
  "segments": [
    {
      "type": "pronunciation",
      "content": "This",
      "start_time": "0.0",
      "end_time": "0.5",
      "confidence": "0.98"
    },
    // More word-level segments
  ],
  "audio_segments": [
    {
      "id": 0,
      "transcript": "This is an example transcription.",
      "start_time": "0.0",
      "end_time": "2.5",
      "items": [0, 1, 2, 3, 4]
    }
  ]
}
```

## Backward Compatibility

The implementation maintains backward compatibility with existing transcription data:

- All methods check for the existence of `audio_segments` before processing them
- When deserializing, `audio_segments` defaults to an empty list if not present
- Existing functionality for word-level segments remains unchanged

## Testing

Comprehensive tests have been added to verify:

- Proper extraction and processing of sentence-level segments
- Serialization and deserialization of audio segments
- Backward compatibility with existing data
- Media type detection for various file formats 