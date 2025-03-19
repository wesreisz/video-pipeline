import boto3
import json
import logging
import os

logger = logging.getLogger()

class S3Utils:
    """Utility class for S3 operations."""
    
    def __init__(self, region=None):
        """
        Initialize the S3 utility.
        
        Args:
            region: AWS region (optional)
        """
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.s3_client = boto3.client('s3', region_name=self.region)
        
    def download_file(self, bucket, key, local_path):
        """
        Download a file from S3.
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            local_path: Local path to save the file
            
        Returns:
            str: Path to the downloaded file
        """
        logger.info(f"Downloading {bucket}/{key} to {local_path}")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Use get_object instead of download_file for better control
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            # Write the content to a local file
            with open(local_path, 'w') as f:
                f.write(content)
                
            logger.info(f"Successfully downloaded {bucket}/{key} to {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            # Add more detailed error information for debugging
            if 'NoSuchKey' in str(e):
                logger.error(f"The file {key} does not exist in bucket {bucket}")
            elif 'AccessDenied' in str(e):
                logger.error(f"Access denied to file {key} in bucket {bucket}. Check IAM permissions.")
            raise
        
    def upload_file(self, local_path, bucket, key):
        """
        Upload a file to S3.
        
        Args:
            local_path: Local path of the file to upload
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            str: S3 URI of the uploaded file
        """
        logger.info(f"Uploading {local_path} to {bucket}/{key}")
        self.s3_client.upload_file(local_path, bucket, key)
        return f"s3://{bucket}/{key}"
        
    def upload_json(self, data, bucket, key):
        """
        Upload JSON data to S3.
        
        Args:
            data: Python object to serialize to JSON
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            str: S3 URI of the uploaded file
        """
        logger.info(f"Uploading JSON data to {bucket}/{key}")
        body = json.dumps(data)
        self.s3_client.put_object(
            Body=body,
            Bucket=bucket,
            Key=key,
            ContentType='application/json'
        )
        return f"s3://{bucket}/{key}"
        
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
        
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error downloading JSON from S3: {str(e)}")
            raise 