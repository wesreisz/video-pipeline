**Prompt: Create Integration Test for Transcribe Handler**

Create an integration test for the transcribe handler Lambda function that:
- Tests the complete request flow with mocked dependencies.
- Verifies correct handling of:
  - Valid S3 events
  - Missing record events
  - Missing bucket/key information
  - Exception scenarios
- Implements proper mocks for:
  - `S3Utils` class
  - `TranscriptionService` class
- Follows project's pytest standards for:
  - File naming and location
  - Test function naming
  - Fixture usage
  - Clear assertions
- Includes appropriate test parameters and edge cases

The test should validate both the happy path and error handling capabilities of the Lambda handler.
