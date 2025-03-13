# Prompt: Setting Up Local Testing for AWS Lambda in Video Pipeline Project

## Task Description

Create a local testing environment for the AWS Lambda Python function that we implemented for the video pipeline project's transcription module. This setup should allow developers to test the Lambda function with simulated AWS services and events without deploying to AWS.

## Requirements

1. Set up a local environment that simulates AWS services using LocalStack
2. Create a test script that can invoke the Lambda handler with simulated S3 events
3. Configure a simple workflow to test the end-to-end functionality
4. Document the testing process with clear instructions for the team

## Local Testing Setup

Implement the following components:

### 1. LocalStack Integration

Set up [LocalStack](https://localstack.cloud/) to simulate AWS services locally:

- Configure S3 buckets for input and output
- Set up environment for Lambda execution
- Create a Docker Compose file for easy startup/shutdown

### 2. Test Script

Create a Python script (`local_test.py`) in the `projects/transcribe-module` directory that:

- Sets up the local environment (creates buckets, etc.)
- Uploads a test audio file to the input bucket
- Creates a simulated S3 event
- Invokes the Lambda handler directly with the event
- Verifies the transcription result in the output bucket

### 3. Makefile Integration

Create a Makefile at the project root with commands for:

- Starting and stopping LocalStack
- Running unit tests
- Running the local integration test
- Setting up the development environment
- Creating sample test files

### 4. AWS SAM Support (Optional)

Add AWS SAM (Serverless Application Model) configuration:

- Create a `template.yaml` file defining the Lambda function and resources
- Set up a sample event file in an `events` directory
- Document SAM CLI commands for local invocation

### 5. Documentation

Update the README with detailed instructions on:

- Different local testing approaches
- Commands to run tests
- Troubleshooting common issues

## Implementation Guidelines

1. The local test script should use the same code as the production Lambda
2. Ensure environment variables are properly set for local testing
3. Build a workflow that's easy for developers to use
4. Include detailed error handling and logging
5. Test all code paths and functionality

## Deliverables

1. `local_test.py` script in the `projects/transcribe-module` directory
2. Makefile with commands for local testing
3. Docker Compose file for running LocalStack
4. Sample events in an `events` directory
5. AWS SAM template (optional)
6. Updated README with testing instructions

## Sample Structure

The test setup should follow this structure:

```
project-root/
├── projects/
│   └── transcribe-module/
│       ├── local_test.py           # Local test script
│       └── specs/
│           └── prompts/
│               └── 3-local-test-setup.md # This file
├── events/
│   └── s3-event.json               # Sample event
├── samples/
│   └── sample.mp3                  # Test audio file
├── Makefile                        # Commands for testing
├── docker-compose.yml              # LocalStack setup
└── template.yaml                   # AWS SAM template
```

## Local Test Script Outline

The test script should follow this general flow:

1. Set up the test environment (create buckets)
2. Upload a test file to the input bucket
3. Create a simulated S3 event
4. Modify the S3 client to point to LocalStack
5. Invoke the Lambda handler with the event
6. Verify the result in the output bucket
7. Report success or failure

## Example Commands

```bash
# Run unit tests
make unit-tests

# Start LocalStack
make start-localstack

# Run local integration test
make test-local

# Full test workflow
make test-workflow
```

Please implement these local testing capabilities to improve the development workflow for the transcription module. This will allow team members to rapidly iterate and verify their changes without waiting for AWS deployments. 