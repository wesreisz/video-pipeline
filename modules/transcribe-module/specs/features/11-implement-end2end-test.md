# Feature: End-to-End Testing for Video Pipeline

## Overview
Create an end-to-end testing solution for the video pipeline that automates the process of verifying the complete pipeline functionality after deployment.

## User Story
As a developer/operator, I want to verify that the complete video transcription pipeline works correctly after deployment, so that I can be confident the system is functioning properly before users interact with it.

## Requirements

1. Create a Python-based end-to-end test that:
   - Uploads a sample audio/video file to the input bucket (use hello-my_name_is_wes.mp4 in the samples folder)
   - Waits for processing to complete
   - Verifies the transcription output
   - Provides clear success/failure feedback

2. Create a shell script that:
   - Simplifies running the test with sensible defaults
   - Automatically extracts bucket names from Terraform outputs
   - Handles errors gracefully

3. Document the testing process thoroughly for future developers

## Implementation Prompt

Create an end-to-end testing solution for our AWS-based video transcription pipeline. The test should verify the entire process works correctly after deployment.

### Python Test Script

Write a Python script named `test_pipeline_e2e.py` that:

1. Takes command-line arguments:
   - Input bucket name
   - Output bucket name
   - Path to sample audio/video file
   - Optional timeout value (default: 300 seconds)
   - Optional cleanup flag to remove test files after completion

2. Uses boto3 to interact with AWS services

3. Implements a test flow that:
   - Uploads the sample file to the input bucket with a unique test ID suffix
   - Waits for the transcription to appear in the output bucket
   - **IMPORTANT**: Only verifies transcription files that contain the SAME test ID as the uploaded file
   - Downloads and verifies the transcription content
   - Outputs clear progress and results information
   - Returns appropriate exit code (0 for success, 1 for failure)

4. Includes robust error handling for potential issues

5. Uses a unique ID for each test run to avoid conflicts:
   - Append this ID to both input and output file names
   - Use this ID to match the output file to the specific input file
   - Do not verify files from previous test runs or files without matching IDs

6. Implements cleanup functionality to:
   - Remove old test files before starting (optional)
   - Clean up test files after completion (when cleanup flag is enabled)
   - Only delete files with the current test ID

### File Naming and Verification Pattern

To ensure consistent verification:

1. Input files should be uploaded with pattern: `media/{base_name}_{test_id}{extension}`
2. When searching for output files, verify they contain the same test ID with pattern: `transcriptions/{base_name}_{test_id}.json`
3. Never verify an output file unless it has the exact same test ID as the input file
4. Use explicit matching against the full test ID, not partial matches or prefix-only matches

### Shell Script Wrapper

Create a bash script named `run_e2e_test.sh` that:

1. Accepts optional parameters:
   - Path to sample file (default: use a file from the samples directory)
   - Timeout value (default: 300 seconds)
   - Cleanup flag to remove test files after completion

2. Uses Terraform outputs to automatically determine:
   - Input bucket name
   - Output bucket name

3. Performs basic validation of prerequisites

4. Runs the Python test script with the appropriate parameters

5. Provides clear, formatted output of the process

### Documentation

Write a README.md file that:

1. Explains how to use the testing tools
2. Describes how the test works
3. Outlines prerequisites
4. Includes troubleshooting information
5. Shows how to integrate with CI/CD pipelines

## Expected Behavior

After implementation, a user should be able to:

1. Run the test with minimal effort after deployment
   ```
   cd modules/transcribe-module/tests/e2e
   ./run_e2e_test.sh
   ```

2. See a clear indication of test progress and results
   ```
   === Starting Video Pipeline E2E Test ===
   
   Uploading sample file...
   ✅ Upload successful
   
   Waiting for transcription to complete...
   Transcription not ready yet, waiting 10 seconds...
   ...
   ✅ Found transcription: transcriptions/hello_my_name_is_wes_12345678.json
   
   Verifying transcription content...
   ✅ Verification passed!
   Transcription text: "Hello, my name is Wes."
   Number of segments: 7
   
   ✅ E2E TEST PASSED: Video pipeline is working correctly!
   ```

3. Get a proper exit code for integration with other tools

4. Optionally clean up test files (both input and output)
   ```
   cd modules/transcribe-module/tests/e2e
   ./run_e2e_test.sh --cleanup
   ```

## Technical Constraints

1. Test script should handle various audio/video formats
2. Test should time out after a reasonable period if no results appear
3. Use file naming that's consistent with our existing patterns
4. Ensure the solution works on both Linux and macOS environments
5. Always verify the exact file that was uploaded in the test, not any other file
6. Maintain a one-to-one relationship between uploaded files and verified files using test IDs

## Acceptance Criteria

- [x] Python test script successfully uploads a sample file and verifies transcription
- [x] Shell script correctly extracts Terraform outputs and runs the Python script
- [x] Documentation is clear and comprehensive
- [x] The test successfully passes when the pipeline is correctly configured
- [x] The test correctly fails when the pipeline is not working
- [x] Code includes proper error handling and reporting
- [x] Test verifies only files with matching test IDs, never other files
- [x] Optional cleanup functionality removes test files to prevent clutter
