import boto3
from loguru import logger
from typing import Optional, List
import csv
import io

class S3Util:
    def __init__(self):
        self._s3_client = None
    
    @property
    def s3_client(self):
        """Lazy initialization of boto3 S3 client."""
        if self._s3_client is None:
            self._s3_client = boto3.client('s3')
        return self._s3_client
    
    def get_access_list(self, bucket: str, key: str) -> Optional[List[str]]:
        """
        Fetch and parse the access list CSV from S3.
        
        Args:
            bucket (str): S3 bucket name
            key (str): S3 object key
            
        Returns:
            Optional[List[str]]: List of authorized email addresses or None if error
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(content))
            return [row[0].strip().lower() for row in csv_reader]
        except Exception as e:
            logger.error(f"Error fetching access list: {str(e)}")
            return None 