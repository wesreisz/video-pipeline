# Lambda Layer Implementation for Embedding Module

## Overview
Update the existing embedding-module to use AWS Lambda layers for dependency management. The module will be split into two components:
1. Lambda Layer (dependencies)
2. Lambda Function (business logic)

## Structure
```
modules/embedding-module/
├── lambda-layer/
│   ├── requirements.txt      # OpenAI dependencies
│   ├── 1-install.sh         # Layer build script
│   ├── 2-package.sh         # Layer packaging script
│   └── README.md            # Layer documentation
├── src/
│   ├── handlers/
│   │   └── lambda_handler.py
│   ├── services/
│   │   └── openai_service.py
│   ├── utils/
│   │   └── config.py        # Configuration management
│   └── requirements.txt     # Lambda function dependencies
├── tests/
└── README.md
```

## Lambda Layer Requirements

### Dependencies
The lambda-layer/requirements.txt must include:
```
openai>=1.0.0
pinecone-client
```

### Build Scripts

#### 1-install.sh
```bash
#!/bin/bash
# Create Python virtual environment
python3.13 -m venv create_layer
source create_layer/bin/activate

# Install dependencies for manylinux2014 compatibility
pip install -r requirements.txt \
    --platform=manylinux2014_x86_64 \
    --only-binary=:all: \
    --target ./create_layer/lib/python3.13/site-packages
```

#### 2-package.sh
```bash
#!/bin/bash
# Create layer structure
mkdir -p python/lib/python3.13/site-packages
cp -r create_layer/lib/python3.13/site-packages/* python/lib/python3.13/site-packages/

# Create deployment package
zip -r layer_content.zip python/
```

## Lambda Function Implementation

### OpenAI Service Configuration
The OpenAI service should be implemented following the official Python client patterns:

```python
from openai import OpenAI
from openai import APITimeoutError, APIError

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=get_openai_api_key(),
            timeout=20.0,
            max_retries=3
        )

    def get_embedding(self, text: str):
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002-v2",
                input=text
            )
            return response.data[0].embedding
        except APITimeoutError as e:
            # Handle timeout errors
            raise
        except APIError as e:
            # Handle API errors
            raise
```

### Environment Variables
Required environment variables for the Lambda function:
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_TIMEOUT`: Request timeout (optional, default 20.0)
- `OPENAI_MAX_RETRIES`: Max retries for failed requests (optional, default 3)

### SQS Integration
The Lambda function will continue to be triggered by SQS messages. The handler should:
1. Process incoming SQS events
2. Extract text content
3. Generate embeddings using OpenAI service
4. Store results in Pinecone

## Deployment Requirements

### Python Runtime
- Python 3.13
- Architecture: arm64 (for cost optimization)
- Memory: Minimum 256MB recommended

### Layer Deployment
1. Build and package the layer using provided scripts
2. Deploy layer to AWS Lambda
3. Note the layer ARN for function configuration

### Function Deployment
1. Package the Lambda function code
2. Deploy with the layer attached
3. Configure environment variables
4. Set up SQS trigger

## Testing

### Local Testing
Test scripts should verify:
1. Layer packaging and structure
2. OpenAI client initialization
3. Embedding generation
4. SQS message processing

### Integration Testing
Verify:
1. Layer attachment to function
2. OpenAI API connectivity
3. End-to-end SQS message processing
4. Pinecone storage

## Security Considerations
1. Store OPENAI_API_KEY in AWS Secrets Manager
2. Use IAM roles with least privilege
3. Enable function URL with proper authentication if needed
4. Configure VPC settings if required

## References
- [AWS Lambda Python Layers Documentation](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html)
- [OpenAI Python Client](https://github.com/openai/openai-python)
- [AWS Lambda Sample Apps](https://github.com/awsdocs/aws-lambda-developer-guide/tree/main/sample-apps/layer-python)
