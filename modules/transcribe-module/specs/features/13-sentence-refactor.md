# Feature: Add Support for Sentence-Level Audio Segments

## Background
AWS Transcribe provides multiple types of speech recognition data beyond just the basic transcription text. Currently, our application captures the word-level segments (items) but doesn't yet support the sentence-level audio segments which provide a more natural grouping of the transcribed content.

## Requirements

1. Extend the TranscriptionResult model to support sentence-level audio segments
2. Update the transcription service to extract sentence-level segments from AWS Transcribe results
3. Process and store sentence-level segments alongside word-level segments
4. Ensure backward compatibility with existing transcription data

## Benefits

- Improved organization of transcription data by grouping words into logical sentences
- Better support for applications that need sentence-level timing information
- More complete representation of AWS Transcribe's output capabilities

## Implementation Considerations

- The TranscriptionResult model will need a new field for audio_segments
- The serialization/deserialization methods need to be updated
- The existing functionality for word-level segments should remain unchanged
- Logging should be enhanced to include information about sentence segments 