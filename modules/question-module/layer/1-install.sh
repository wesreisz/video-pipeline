#!/bin/bash

# Exit on error
set -e

# Clean up any existing files
rm -rf python

# Create the Python package directory
mkdir -p python

# Create and activate virtual environment
python3.11 -m pip install \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --target ./python \
    -r requirements.txt

# Remove unnecessary files to reduce layer size
find ./python -type d -name "tests" -exec rm -rf {} +
find ./python -type d -name "__pycache__" -exec rm -rf {} +
find ./python -type f -name "*.pyc" -delete
find ./python -type f -name "*.pyo" -delete

echo "Layer dependencies installed successfully."
echo "Layer size: $(du -sh python | cut -f1)" 