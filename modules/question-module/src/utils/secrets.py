import json
import os
import logging
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError

# Set up basic logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Global cache for secrets at the module level
_SECRETS_CACHE: Dict[str, str] = {}
_SECRETS_LOADED = False
_SECRETS_SERVICE_INSTANCE: Optional['SecretsService'] = None
_secrets_service = None

class SecretsService:
    """Service for managing secrets using AWS Secrets Manager with environment variable fallback"""
    
    def __init__(self):
        """Initialize the secrets service with lazy loading."""
        self._client = None  # Lazy initialization
        self._secret_name = f"{os.environ.get('ENVIRONMENT', 'dev')}-video-pipeline-secrets"
        self._use_env_fallback = os.environ.get('USE_ENV_FALLBACK', 'true').lower() == 'true'
    
    @property
    def client(self):
        """Lazy initialization of boto3 client."""
        if self._client is None:
            self._client = boto3.client('secretsmanager')
        return self._client
    
    def _load_secrets(self) -> None:
        """
        Load all secrets from AWS Secrets Manager into the global cache.
        This is done once per Lambda container lifetime.
        """
        global _SECRETS_LOADED, _SECRETS_CACHE
        
        if _SECRETS_LOADED:
            return
            
        try:
            response = self.client.get_secret_value(SecretId=self._secret_name)
            secrets_dict = json.loads(response['SecretString'])
            _SECRETS_CACHE.update(secrets_dict)
            _SECRETS_LOADED = True
            logger.info("Successfully loaded secrets into cache")
        except ClientError as e:
            logger.error(f"Failed to load secrets from AWS Secrets Manager: {str(e)}")
            if not self._use_env_fallback:
                raise
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a specific secret value by key.
        First checks the cache, then AWS Secrets Manager, then falls back to environment variables if configured.
        
        Args:
            key: The key of the secret to retrieve
            
        Returns:
            The secret value if found, None otherwise
        """
        # First check the cache
        if key in _SECRETS_CACHE:
            return _SECRETS_CACHE[key]
        
        try:
            # Load secrets if not already loaded
            self._load_secrets()
            
            # Check cache again after loading
            if key in _SECRETS_CACHE:
                return _SECRETS_CACHE[key]
            
            # If still not found and fallback is enabled, try environment variables
            if self._use_env_fallback:
                env_key = key.upper()
                if env_value := os.environ.get(env_key):
                    logger.info(f"Using environment variable fallback for {key}")
                    _SECRETS_CACHE[key] = env_value  # Cache the environment value
                    return env_value
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving secret {key}: {str(e)}")
            return None
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from cache or secrets"""
        return self.get_secret('video-pipeline-api-key')
    
    def get_access_list_url(self) -> Optional[str]:
        """Get access list URL from cache or secrets"""
        return self.get_secret('access_list_url')
    
    def invalidate_cache(self) -> None:
        """
        Invalidate the secrets cache.
        Useful for testing or when secrets need to be reloaded.
        """
        global _SECRETS_LOADED, _SECRETS_CACHE
        _SECRETS_LOADED = False
        _SECRETS_CACHE.clear()
        logger.info("Secrets cache invalidated")

def get_secrets_service() -> SecretsService:
    """Get or create a singleton SecretsService instance."""
    global _secrets_service
    if _secrets_service is None:
        _secrets_service = SecretsService()
    return _secrets_service 