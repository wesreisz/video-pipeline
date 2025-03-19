# Media Chunking Module

This module is part of the video pipeline project and handles chunking of media files into segments using AWS Lambda and S3.

## Overview

The chunking module works as follows:

1. Media files are processed (input from S3 bucket or another service)
2. The Lambda function:
   - Processes the media file
   - Divides it into logical chunks or segments
   - Uploads the chunking result to the output bucket as JSON

## Getting Started

### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 0.14
- Python 3.9+
- Docker (for local testing with LocalStack)

### Deployment

#### Option 1: Using the Automated Deployment Script (Recommended)

The project includes an automated deployment script that handles all the steps required to build, test, and deploy the module to the dev environment:

```bash
# Navigate to the dev environment directory
cd infra/environments/dev

# Run the deployment script
./deploy.sh
```

#### Option 2: Manual Deployment

If you prefer to deploy manually, follow these steps:

1. Set up the module-specific virtual environment:
   ```
   cd modules/chunking-module
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
   zip -r infra/build/chunking_lambda.zip modules/chunking-module/src/
   ```

5. Deploy to the dev environment:
   ```
   cd infra/environments/dev
   terraform init
   terraform plan -out=tfplan
   terraform apply "tfplan"
   ```

## Project Structure

- `src/`: Lambda function code
  - `handlers/`: Lambda entry points
  - `services/`: Business logic for chunking
  - `models/`: Data structures
  - `utils/`: Helper functions and utilities
- `tests/`: Unit tests
- `specs/`: Design documents and specifications

## Testing

### Unit and Integration Tests

Run tests using pytest (recommended):
```bash
cd modules/chunking-module
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
# Run tests with pytest
python -m pytest -xvs tests/
```

## Environment Variables

The Lambda function uses the following environment variables:

- `CHUNKING_OUTPUT_BUCKET`: The S3 bucket where chunking results are stored

## Contributing

Follow the project's code style and ensure that tests pass before submitting pull requests. Always use the deploy.sh script to verify your changes work in the dev environment. 