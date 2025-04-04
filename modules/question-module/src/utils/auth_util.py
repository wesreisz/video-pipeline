import csv
import boto3
from datetime import datetime
from typing import List, Optional
from loguru import logger
from utils.secrets import get_secrets_service
from urllib.parse import urlparse

class AuthUtil:
    """Utility class for handling authorization."""
    
    def __init__(self):
        """Initialize AuthUtil with empty access list."""
        self._authorized_emails: List[str] = []
        self._secrets_service = get_secrets_service()
        self._s3_client = boto3.client('s3')
        self._last_refresh: Optional[datetime] = None
        self._cache_ttl: int = 300  # 5 minutes in seconds
        logger.info("AuthUtil initialized, loading access list...")
        self._load_access_list()
    
    def _is_cache_stale(self) -> bool:
        """Check if the cache is stale (older than 5 minutes)."""
        if not self._last_refresh:
            return True
        return (datetime.now() - self._last_refresh).total_seconds() > self._cache_ttl
    
    def _load_access_list(self) -> None:
        """Load the access list from S3."""
        try:
            access_list_url = self._secrets_service.get_access_list_url()
            logger.info(f"Loading access list from URL: {access_list_url}")
            
            if not access_list_url:
                logger.error("Access list URL not configured or invalid")
                return
            
            # Parse S3 URL to get bucket and key
            parsed_url = urlparse(access_list_url)
            bucket = parsed_url.netloc.split('.')[0]  # Extract bucket name from hostname
            key = parsed_url.path.lstrip('/')  # Remove leading slash from path
            
            logger.info(f"Fetching access list from bucket: {bucket}, key: {key}")
            
            # Get the file from S3
            response = self._s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8').splitlines()
            
            # Parse CSV content
            reader = csv.reader(content)
            self._authorized_emails = [row[0].strip().lower() for row in reader if row]
            
            # Update last refresh timestamp
            self._last_refresh = datetime.now()
            
            logger.info(f"Loaded {len(self._authorized_emails)} authorized emails")
            logger.debug(f"Current authorized emails: {self._authorized_emails}")
            
        except Exception as e:
            logger.error(f"Error loading access list: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Error details: {e.response}")
    
    def is_authorized(self, email: str) -> bool:
        """
        Check if an email is authorized.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if email is authorized, False otherwise
        """
        # Check if cache is stale and refresh if needed
        if self._is_cache_stale():
            logger.info("Cache is stale, refreshing access list...")
            self._load_access_list()
            
        email = email.lower()
        is_auth = email in self._authorized_emails
        logger.info(f"Authorization check for {email}: {'authorized' if is_auth else 'unauthorized'}")
        logger.debug(f"Current authorized emails: {self._authorized_emails}")
        return is_auth

    def refresh_access_list(self) -> None:
        """Force refresh the access list from S3."""
        logger.info("Refreshing access list...")
        self._load_access_list() 