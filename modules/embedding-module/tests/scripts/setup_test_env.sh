#!/bin/bash

# Exit on any error
set -e

# Check if test file is provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error: API key and test file are required"
    echo "Usage: $0 <api-key> <test-file>"
    echo "Example for OpenAI: $0 sk-xxx tests/integration/test_openai_service_integration.py"
    echo "Example for Pinecone: $0 xxxx-xxx tests/integration/test_pinecone_service_integration.py"
    exit 1
fi

# Default environment
export ENVIRONMENT="dev"

# Enable live tests
export RUN_LIVE_TESTS=1

# Set log level for testing
export LOG_LEVEL="INFO"

# Enable environment variable fallback
export USE_ENV_FALLBACK=true

# Determine which test we're running and set appropriate API key
if [[ "$2" == *"openai"* ]]; then
    export OPENAI_API_KEY="$1"
    # Set OpenAI Organization ID that we verified works
    export OPENAI_ORG_ID="org-b6y2SlhOMQnynny57KMpe8Bk"
elif [[ "$2" == *"pinecone"* ]]; then
    export PINECONE_API_KEY="$1"
    # Set Pinecone environment (default to GCP)
    export PINECONE_ENVIRONMENT="us-west1-gcp"
else
    echo "Error: Test file must contain either 'openai' or 'pinecone' in its name"
    exit 1
fi

# Set AWS credentials for local testing
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
export AWS_DEFAULT_REGION="us-east-1"

# Check if we're running in CI/CD
if [ -n "$CI" ]; then
    echo "Running in CI/CD environment"
else
    echo "Running in local environment"
fi

# Print setup status
echo "Test environment configured:"
echo "- ENVIRONMENT: $ENVIRONMENT"
echo "- RUN_LIVE_TESTS: $RUN_LIVE_TESTS"
echo "- LOG_LEVEL: $LOG_LEVEL"
echo "- USE_ENV_FALLBACK: $USE_ENV_FALLBACK"

# Print API key info based on test type
if [[ "$2" == *"openai"* ]]; then
    echo "- OPENAI_API_KEY: ***${OPENAI_API_KEY: -4}"
    echo "- OpenAI Organization ID: $OPENAI_ORG_ID"
elif [[ "$2" == *"pinecone"* ]]; then
    echo "- PINECONE_API_KEY: ***${PINECONE_API_KEY: -4}"
    echo "- Pinecone Environment: $PINECONE_ENVIRONMENT"
fi

echo "- AWS credentials set for local testing"

# Run the tests
python -m pytest "$2" -v 