#!/usr/bin/env python3
"""
Pytest test file for S3Utils.

This module contains pytest tests for the S3Utils class.
"""

import os
import json
import logging
import pytest
import boto3
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_s3_utils')

# Import S3Utils
from utils.s3_utils import S3Utils

# Define fixtures specific to this test file
@pytest.fixture(scope="module")
def temp_dir():
    """Create a temporary directory for downloads."""
    dir_path = "/tmp/transcriptions"
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

@pytest.fixture(scope="module")
def s3_utils():
    """Create an instance of S3Utils."""
    return S3Utils()

@pytest.mark.integration
def test_download_file(s3_bucket, s3_key, temp_dir, s3_utils):
    """Test downloading a file from S3 using download_file method."""
    # Skip test if bucket or key not provided
    if not s3_bucket or not s3_key:
        pytest.skip("Skipping test_download_file: bucket or key not provided")
    
    logger.info(f"Testing download_file method with bucket={s3_bucket}, key={s3_key}")
    
    # Generate a local filename from the S3 key
    filename = os.path.basename(s3_key)
    local_path = os.path.join(temp_dir, filename)
    
    # Try downloading with download_file
    try:
        # Remove the file if it already exists
        if os.path.exists(local_path):
            os.remove(local_path)
        
        # Download the file
        downloaded_path = s3_utils.download_file(s3_bucket, s3_key, local_path)
        
        # Verify the download
        assert downloaded_path == local_path, f"Expected path {local_path}, got {downloaded_path}"
        assert os.path.exists(local_path), f"Downloaded file {local_path} does not exist"
        assert os.path.getsize(local_path) > 0, f"Downloaded file {local_path} is empty"
        
        logger.info(f"Successfully downloaded file to {local_path}")
        
        # Try to parse the file as JSON if it has a .json extension
        if s3_key.lower().endswith('.json'):
            try:
                with open(local_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Successfully parsed {local_path} as JSON")
                
                # Log some basic info about the JSON structure
                if isinstance(data, dict):
                    logger.info(f"JSON contains {len(data)} top-level keys")
                    for key in list(data.keys())[:5]:  # Log first 5 keys
                        logger.info(f"  Key: {key}")
                elif isinstance(data, list):
                    logger.info(f"JSON contains a list with {len(data)} items")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"File {local_path} is not valid JSON: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error testing download_file: {str(e)}")
        raise
    
    return local_path

@pytest.mark.integration
def test_download_json(s3_bucket, s3_key, s3_utils):
    """Test downloading and parsing a JSON file from S3 using download_json method."""
    # Skip test if bucket or key not provided
    if not s3_bucket or not s3_key:
        pytest.skip("Skipping test_download_json: bucket or key not provided")
    
    # Skip if the key doesn't end with .json
    if not s3_key.lower().endswith('.json'):
        pytest.skip(f"Skipping test_download_json: key {s3_key} is not a JSON file")
    
    logger.info(f"Testing download_json method with bucket={s3_bucket}, key={s3_key}")
    
    # Try downloading and parsing with download_json
    try:
        # Download and parse the JSON
        data = s3_utils.download_json(s3_bucket, s3_key)
        
        # Verify the result
        assert data is not None, "download_json returned None"
        assert isinstance(data, (dict, list)), f"Expected dict or list, got {type(data)}"
        
        logger.info("Successfully downloaded and parsed JSON")
        
        # Log some basic info about the JSON structure
        if isinstance(data, dict):
            logger.info(f"JSON contains {len(data)} top-level keys")
            for key in list(data.keys())[:5]:  # Log first 5 keys
                logger.info(f"  Key: {key}")
                
            # If it's a transcription file, check for expected keys
            if 'results' in data and 'transcripts' in data.get('results', {}):
                transcripts = data['results']['transcripts']
                logger.info(f"Found {len(transcripts)} transcripts")
                for i, transcript in enumerate(transcripts[:3]):  # Show first 3 transcripts
                    logger.info(f"  Transcript {i+1}: {transcript.get('transcript', 'N/A')[:100]}...")
                    
        elif isinstance(data, list):
            logger.info(f"JSON contains a list with {len(data)} items")
            for i, item in enumerate(data[:3]):  # Show first 3 items
                if isinstance(item, dict):
                    logger.info(f"  Item {i+1}: contains {len(item)} keys")
                else:
                    logger.info(f"  Item {i+1}: {type(item)}")
                    
        return data
                
    except Exception as e:
        logger.error(f"Error testing download_json: {str(e)}")
        raise 