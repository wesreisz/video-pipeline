import boto3
import json
import logging
import datetime
from boto3 import client

logger = logging.getLogger()

class S3Utils:
    """Utility class for S3 operations"""
    
    def __init__(self):
        """Initialize with boto3 S3 client"""
        self.s3_client = boto3.client('s3')
    
    def download_file(self, bucket, key, local_path):
        """
        Download a file from S3
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            local_path (str): Local path to save the file
        """
        logger.info(f"Downloading s3://{bucket}/{key} to {local_path}")
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
    
    def download_json(self, bucket, key):
        """
        Download and parse a JSON file from S3
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key of JSON file
            
        Returns:
            dict: Parsed JSON content
        """
        logger.info(f"Downloading and parsing JSON from s3://{bucket}/{key}")
        
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    
    def get_current_timestamp(self):
        """
        Generate current timestamp in ISO format
        
        Returns:
            str: ISO-formatted timestamp
        """
        return datetime.datetime.now().isoformat()
        
    def get_object_metadata(self, bucket, key):
        """
        Get metadata from an S3 object
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            
        Returns:
            dict: Object metadata or empty dict if metadata not found
        """
        try:
            logger.info(f"Fetching metadata for s3://{bucket}/{key}")
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            return response.get('Metadata', {})
        except Exception as e:
            logger.warning(f"Failed to get metadata for {bucket}/{key}: {str(e)}")
            return {} 