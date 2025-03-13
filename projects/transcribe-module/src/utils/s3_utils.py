import boto3
import json
import logging
from datetime import datetime

logger = logging.getLogger()

class S3Utils:
    """Utility class for S3 operations"""
    
    def __init__(self):
        """Initialize with boto3 S3 client"""
        self.s3_client = boto3.client('s3')
    
    def download_file(self, bucket, key, local_path):
        """
        Download a file from S3 to a local path
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            local_path (str): Local file path to save to
        """
        logger.info(f"Downloading {bucket}/{key} to {local_path}")
        self.s3_client.download_file(bucket, key, local_path)
    
    def upload_file(self, local_path, bucket, key):
        """
        Upload a file to S3
        
        Args:
            local_path (str): Local file path to upload
            bucket (str): S3 bucket name
            key (str): S3 object key
        """
        logger.info(f"Uploading {local_path} to {bucket}/{key}")
        self.s3_client.upload_file(local_path, bucket, key)
    
    def upload_json(self, bucket, key, data):
        """
        Upload JSON data to S3
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            data (dict): Data to serialize as JSON and upload
        """
        logger.info(f"Uploading JSON data to {bucket}/{key}")
        json_data = json.dumps(data)
        self.s3_client.put_object(
            Body=json_data,
            Bucket=bucket,
            Key=key,
            ContentType='application/json'
        )
    
    def get_current_timestamp(self):
        """
        Get current timestamp in ISO format
        
        Returns:
            str: ISO-formatted timestamp
        """
        return datetime.utcnow().isoformat() 