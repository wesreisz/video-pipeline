# Video Pipeline Project Setup

Create a video processing pipeline project with the following specifications:

## Project Overview
Create a serverless video processing pipeline that:
1. Transcribes video/audio content
2. Chunks the transcriptions
3. Creates embeddings for the chunks
4. Provides a question-answering interface

## Technology Stack
- Python 3.11 for Lambda functions
- Terraform for infrastructure (compatible with AWS provider >= 5.0)
- AWS Services:
  - Lambda
  - S3
  - API Gateway
  - Step Functions
  - Transcribe
  - OpenAI for embeddings
  - Pinecone for vector storage

## Project Structure
Create the following directory structure:

```
video-pipeline/
├── infra/
│   ├── modules/
│   │   ├── lambda/           # Base Lambda module
│   │   ├── s3/              # S3 bucket configurations
│   │   ├── transcribe-module/
│   │   ├── chunking-module/
│   │   ├── embedding-module/
│   │   └── question-module/
│   └── environments/
│       └── dev/             # Development environment
├── modules/
│   ├── transcribe-module/
│   │   ├── specs/          # Module specifications
│   │   ├── src/
│   │   │   ├── handlers/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── tests/
│   ├── chunking-module/     # Similar structure as transcribe
│   ├── embedding-module/    # Similar structure as transcribe
│   └── question-module/     # Similar structure as transcribe
└── samples/                 # Sample media files for testing
```

## Module Requirements

### Common Requirements for All Modules
- Virtual environment management
- Unit tests using pytest
- Error handling and logging
- AWS Lambda handler structure
- Requirements.txt and dev-requirements.txt

### Specific Module Requirements

1. Transcribe Module
   - Handle S3 events for new media files
   - AWS Transcribe integration
   - Support for metadata handling

2. Chunking Module
   - Process transcription results
   - Implement chunking logic
   - Store chunks in S3

3. Embedding Module
   - OpenAI API integration
   - Pinecone vector storage
   - Process chunks and create embeddings

4. Question Module
   - REST API endpoint via API Gateway
   - Question processing logic
   - Email-based response system

## Infrastructure Requirements

### Base Lambda Module
- Support for environment variables
- IAM role and policy management
- Layer support
- Configurable timeout and memory

### Lambda Layer Management
- Shared layer for common dependencies
- Layer structure:
  ```
  layer/
  ├── 1-install.sh          # Script to install dependencies
  ├── 2-package.sh         # Script to package layer
  ├── requirements.txt     # Layer dependencies
  └── python/              # Python packages directory
  ```
- Layer packaging requirements:
  - All dependencies must be Linux/x86_64 compatible
  - Package only required dependencies
  - Maximum layer size consideration (50MB zipped)
  - Python packages must be in 'python/' directory
- Layer deployment:
  - Version management
  - Reuse across multiple functions
  - Region compatibility
  - Architecture compatibility (x86_64)

### Environment Configuration
- Separate state management
- Environment-specific variables
- Resource naming conventions

### Deployment
- Deployment script (deploy.sh)
- Environment setup
- Test execution
- Infrastructure deployment

## Testing Requirements
- Unit tests for all modules
- Integration tests where applicable
- End-to-end test script
- Test coverage requirements

## Security Requirements
- IAM least privilege access
- Environment variable management
- API authentication
- Secure storage of sensitive data

## Documentation Requirements
- Module-specific documentation
- API documentation
- Setup and deployment instructions
- Testing instructions

## Development Guidelines
1. Use absolute imports from module root
2. No src in import paths
3. Consistent error handling
4. Standard logging format
5. Type hints in Python code
6. Terraform best practices

## Dependencies
List of key dependencies and their versions:
- pytest
- python-json-logger
- pydantic
- openai
- pinecone-client
- boto3
- loguru

Create this project structure with placeholder files and basic implementations that can be expanded upon later.
