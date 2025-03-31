```mermaid
flowchart TD
   flowchart TD
    Admin["Admin"] -- ① Uploads file --> B["Amazon S3"]

    B -- ② Triggers --> D["Transcription Module"]
    subgraph L1["Transcription"]
         D
         E["AWS Transcribe Service"]
         D -- ③ Uses --> E
    end
    D -- ④ Writes transcription back to --> B

    B -- ⑤ Notifies --> J["Chunking Module"]
    subgraph L2["Chunking"]
         J
         J -- Loads text chunks into --> G["SQS Queue"]
    end

    G -- ⑥ Invokes in development --> EM[Embedding]
    subgraph EM["Embedding"]
         H["Text Embedding Module"]
         H -- ⑧ Stores vectors in --> P["Pinecone Vector DB"]
    end

    H -- ⑦ Uses --> O["OpenAI Embedding Service"]

    P -- ⑨ Responds to queries from --> Q["ChatGPT"]

    subgraph QM["Question Module"]
        Q
    end

    Q -- ⑩ Uses --> O

    EndUser["User"] -- ⑪ Asks question --> Q

    style Admin fill:#d1eaff,stroke:#007acc,stroke-width:2px,rx:10,ry:10
    style EndUser fill:#d1eaff,stroke:#007acc,stroke-width:2px,rx:10,ry:10


```

# Video Pipeline

A serverless audio/video processing pipeline designed to automate transcription and semantic chunking of media content. This pipeline is part of the InfoQ Certified Architect in Emerging Technologies (ICAET) certification at QCon London.

## Project Overview

This project implements a modern serverless architecture for processing audio and video files, featuring:

- Automatic transcription of audio/video files using AWS Transcribe
- Semantic chunking of transcriptions for improved content organization
- Event-driven architecture using EventBridge and Step Functions
- Infrastructure as Code using Terraform
- Comprehensive testing suite including unit, integration, and end-to-end tests

## Architecture

The video processing pipeline implements an event-driven serverless architecture on AWS:

### Core Components

1. **Storage Layer**
   - S3 buckets for input media files and processed outputs
   - Versioning enabled for data integrity
   - Encryption at rest for security compliance

2. **Event Processing**
   - EventBridge for standardized event routing (using EventBridge format)
   - Step Functions for workflow orchestration
   - SQS queues for reliable message processing

3. **Processing Modules**
   - Transcribe Module: Handles audio/video transcription
   - Chunking Module: Processes transcriptions into semantic chunks
   - Embedding Module: Creates embeddings using OpenAI
   - Lambda functions for serverless execution

### Event Flow

1. File upload triggers an S3 event
2. EventBridge routes the event to appropriate services
3. Step Functions orchestrate the processing workflow
4. Results are stored back in S3

## Project Structure

```
video-pipeline/
├── infra/                 # Infrastructure as Code
│   ├── environments/      # Environment-specific configs (dev, prod)
│   │   ├── dev/
│   │   └── prod/
│   └── modules/           # Reusable Terraform modules
│
├── modules/               # Service Implementations
│   ├── transcribe-module/ # Audio/video transcription
│   ├── chunking-module/   # Semantic chunking
│   └── embedding-module/  # Vector embeddings
│
├── tests/                 # Test Suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
└── samples/               # Sample media files
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.9 or higher
- Terraform ≥ 5.91.0
- Docker (for local testing)
- Make (optional, for build scripts)


## Getting Started

### Local Development Setup

1. Clone and setup the repository:
   ```bash
   git clone <repository-url>
   cd video-pipeline
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

### Deployment

1. Build the modules:
   ```bash
   rm -rf ./infra/build
   mkdir -p ./infra/build
   zip -r ./infra/build/transcribe-module.zip ./modules/transcribe-module
   zip -r ./infra/build/chunking-module.zip ./modules/chunking-module
   zip -r ./infra/build/embedding-module.zip ./modules/embedding-module
   ```

2. Deploy infrastructure:
   ```bash
   cd infra/environments/dev
   terraform init
   terraform fmt
   terraform validate
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

## Testing

### Running Tests

1. Unit Tests:
   ```bash
   python -m pytest tests/unit -v
   ```

2. Integration Tests:
   ```bash
   python -m pytest tests/integration -v
   ```

3. End-to-End Tests:
   ```bash
   cd tests/e2e
   ./run_e2e_test.sh
   ```

### E2E Test Options

```bash
./run_e2e_test.sh [OPTIONS]

Options:
  --input-bucket BUCKET   Specify input S3 bucket
  --output-bucket BUCKET  Specify output S3 bucket
  --file FILE            Path to sample audio/video file
  --timeout SECONDS      Maximum wait time (default: 300s)
  --cleanup             Remove test artifacts after completion
  --venv PATH           Path to Python virtual environment
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow coding standards and write tests
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contact

Wesley Reisz