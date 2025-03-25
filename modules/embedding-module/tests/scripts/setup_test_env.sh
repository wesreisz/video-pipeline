#!/bin/bash

# Check if API key is provided
if [ -z "$1" ]; then
    echo "Usage: source setup_test_env.sh <your-openai-api-key>"
    echo "Please provide your OpenAI API key as an argument"
    exit 1
fi

# Export environment variables
export OPENAI_API_KEY="$1"
export RUN_LIVE_TESTS=1

echo "Environment variables set:"
echo "OPENAI_API_KEY=***${OPENAI_API_KEY: -4}"
echo "RUN_LIVE_TESTS=$RUN_LIVE_TESTS" 