# Shared Libraries

This directory contains shared code that is used across multiple modules in the video pipeline project.

## Directory Structure

- `utils/`: Utility functions and classes
  - `s3_utils.py`: Utility for S3 operations (upload, download, etc.)

## Usage

To use the shared libraries in your module, add the following import logic:

```python
import os
import sys

# Add project root to Python path for imports
try:
    # For modules within the video pipeline project
    # Adjust the relative path as needed based on your module's location
    module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    if module_path not in sys.path:
        sys.path.append(module_path)
    from modules.shared_libs.utils import S3Utils
except ImportError:
    print("WARNING: Cannot import from shared_libs.")
```

## Available Utilities

### S3Utils

The `S3Utils` class provides common operations for interacting with AWS S3:

- `download_file(bucket, key, local_path)`: Download a file from S3
- `upload_file(local_path, bucket, key)`: Upload a file to S3
- `upload_json(data, bucket, key)`: Serialize and upload JSON data to S3

Example usage:

```python
from modules.shared_libs.utils import S3Utils

s3_utils = S3Utils()
s3_utils.download_file('my-bucket', 'path/to/file.json', '/tmp/file.json')
``` 