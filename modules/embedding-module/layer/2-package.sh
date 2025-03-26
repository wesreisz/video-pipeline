#!/bin/bash

# Exit on error
set -e

# Create deployment package
zip -r layer_content.zip python/

echo "Layer packaged successfully as layer_content.zip" 