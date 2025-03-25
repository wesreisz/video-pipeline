#!/bin/bash

# Exit on error
set -e

# Create Python virtual environment
python3.13 -m venv create_layer
source create_layer/bin/activate

# Install dependencies for manylinux2014 compatibility
pip install -r requirements.txt \
    --platform=manylinux2014_x86_64 \
    --only-binary=:all: \
    --target ./create_layer/lib/python3.13/site-packages

echo "Layer dependencies installed successfully" 