# Video Pipeline

A serverless audio/video processing pipeline designed to automate transcription and other media processing. This pipeline will be used as part of the InfoQ Certified Architect in Emerging Technologies (ICAET) certification at QCon London. 

## Project Overview

This project implements a serverless architecture for processing audio and video files. The core functionality includes:

- Automatic transcription of audio files
- Scalable infrastructure using AWS services
- Modular design for easy extension with additional processing capabilities

## Architecture

### Video Processing Pipeline

The video processing pipeline uses AWS services to process media files through a serverless architecture:

#### Previous Architecture (S3 Direct Events)
- S3 buckets for input media, transcription output, and chunking output
- Lambda functions for transcription and chunking
- S3 event notifications to directly trigger Lambda functions in sequence

#### New Architecture (EventBridge + Step Functions)
- S3 buckets for input media, transcription output, and chunking output
- CloudTrail to capture S3 object creation events
- EventBridge to route events from CloudTrail to Step Functions
- Step Functions state machine to orchestrate the workflow:
  1. Transcribe Module: Processes audio/video files and creates transcriptions
  2. Wait for Transcription: Allows time for the transcription process to complete
  3. Chunking Module: Processes transcription files to create semantic chunks

This architecture provides several advantages:
- Better error handling and retry capabilities
- Visualization of the workflow through the Step Functions console
- More robust orchestration with conditional paths based on task outcomes
- Easier monitoring and debugging of the pipeline

#### Workflow Diagram

```
┌───────────┐     ┌────────────┐     ┌──────────────┐     ┌─────────────────┐
│           │     │            │     │              │     │                 │
│  Upload   │────▶│ CloudTrail │────▶│ EventBridge  │────▶│  Step Functions │
│  to S3    │     │            │     │              │     │                 │
└───────────┘     └────────────┘     └──────────────┘     └────────┬────────┘
                                                                    │
                                                                    ▼
┌───────────┐                                               ┌─────────────────┐
│           │                                               │                 │
│ Chunking  │◀──────────────────────────────────────────────│  Transcribe    │
│ Output    │                                               │  Module        │
└───────────┘                                               └─────────────────┘
      ▲                                                              │
      │                                                              ▼
      │                                                     ┌─────────────────┐
      │                                                     │                 │
      └─────────────────────────────────────────────────────│  Chunking      │
                                                            │  Module        │
                                                            └─────────────────┘
```

### Deployment

The infrastructure is deployed using Terraform modules for maintainability and reuse.

To deploy:

1. Navigate to the environment directory (e.g., `infra/environments/dev`)
2. Run `terraform init` and `terraform plan`
3. Deploy with `terraform apply`

## Project Structure

- **infra/**: Infrastructure as code
  - `modules/`: Reusable infrastructure modules
  - `environments/`: Environment-specific configurations

- **modules/**: Individual service implementations
  - `transcribe-module/`: Service for transcribing audio files

- **samples/**: Sample media files for testing

- **Configuration files:**
  - `requirements.txt`: Python dependencies
  - `dev-requirements.txt`: Development-specific Python dependencies
  - `template.yaml`: SAM template for AWS resources

## Prerequisites

- Python 3.9+
- AWS CLI
- AWS SAM CLI
- Docker (for local testing)

## Getting Started

### Installation

1. Clone the repository
   ```
   git clone <repository-url>
   cd video-pipeline
   ```

2. Set up a Python virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   pip install -r dev-requirements.txt  # For development
   ```

### Deployment

To deploy the complete application, follow these steps:

1. Build the application
   ```
   # Clean the build directory if it exists
   rm -rf ./infra/build
   
   # Create a new build directory
   mkdir -p ./infra/build
   
   # Package the Lambda function code
   zip -r ./infra/build/transcribe-module.zip ./modules/transcribe-module
   ```

2. Deploy infrastructure using Terraform
   ```
   # Navigate to the desired environment directory
   cd infra/environments/dev
   
   # Initialize Terraform
   terraform init
   
   # Plan the deployment to see what will change
   terraform plan -out=tfplan
   
   # Apply the changes
   terraform apply tfplan
   ```

3. Verify deployment
   ```
   # List the created resources
   terraform output
   ```

4. To destroy the infrastructure when no longer needed
   ```
   terraform destroy
   ```

## Testing

### Setting Up the Test Environment

1. Navigate to the transcribe module directory:
   ```bash
   cd modules/transcribe-module
   ```

2. Create a virtual environment if it doesn't exist:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

4. Install test dependencies:
   ```bash
   pip install -r dev-requirements.txt
   ```

### Running the Test Suite

Run the complete test suite (unit tests and integration tests):
```bash
python -m pytest -v tests/
```

Run only unit tests:
```bash
python -m pytest -v tests/ --exclude=tests/e2e --exclude=tests/integration
```

Run only integration tests:
```bash
python -m pytest -v tests/integration/
```

### Running End-to-End Tests

The end-to-end tests verify the entire deployed pipeline on AWS.

1. Navigate to the e2e test directory:
   ```bash
   cd tests/e2e
   ```

2. Run the end-to-end test script:
   ```bash
   ./run_e2e_test.sh --cleanup
   ```

   Options:
   - `--cleanup`: Clean up test files after completion
   - `--file PATH`: Specify a custom sample file
   - `--timeout SECONDS`: Set a custom timeout (default: 300 seconds)

Note: End-to-end tests require active AWS credentials and a deployed infrastructure.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contact

Wesley Reisz