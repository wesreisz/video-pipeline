#!/bin/bash

# Exit on any error
set -e

# Check if API key is provided
if [ -z "$1" ]; then
    echo "Error: OpenAI API key not provided"
    echo "Usage: $0 <openai-api-key>"
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

# Set OpenAI API key
export OPENAI_API_KEY="$1"

# Set OpenAI Organization ID that we verified works
export OPENAI_ORG_ID="org-b6y2SlhOMQnynny57KMpe8Bk"

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
echo "- OPENAI_API_KEY: ***${OPENAI_API_KEY: -4}"
echo "- OpenAI Organization ID: $OPENAI_ORG_ID"
echo "- AWS credentials set for local testing"

# Run the tests if a test file is provided
if [ ! -z "$2" ]; then
    python -m pytest "$2" -v
else
    echo "Environment variables set. You can now run your tests."
    echo "Example: python -m pytest tests/integration/test_openai_service_integration.py -v"
fi 