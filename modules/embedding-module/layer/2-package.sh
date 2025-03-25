#!/bin/bash

# Exit on error
set -e

# Create layer structure
mkdir -p python/lib/python3.13/site-packages
cp -r create_layer/lib/python3.13/site-packages/* python/lib/python3.13/site-packages/

# Create deployment package
zip -r layer_content.zip python/

echo "Layer packaged successfully as layer_content.zip" 