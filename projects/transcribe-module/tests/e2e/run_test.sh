#!/bin/bash
# Script to run the end-to-end test for AWS Transcribe module

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install boto3 requests

# Set AWS region if not already set
if [ -z "$AWS_REGION" ]; then
    export AWS_REGION=us-east-1
fi

# Run the test
echo "Running end-to-end test..."
python test_transcribe_e2e.py "$@"

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ End-to-end test completed successfully!"
else
    echo "❌ End-to-end test failed!"
fi

exit $EXIT_CODE 