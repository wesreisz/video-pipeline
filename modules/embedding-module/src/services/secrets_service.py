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

class SecretsService:
    """Service for managing secrets using AWS Secrets Manager with environment variable fallback"""
    
    def __init__(self):
        self._secrets_cache: Dict[str, Dict] = {}
        self._client = None  # Initialize client lazily
        self._secret_name = f"{os.environ.get('ENVIRONMENT', 'dev')}-video-pipeline-secrets"
        self._use_env_fallback = os.environ.get('USE_ENV_FALLBACK', 'true').lower() == 'true'
    
    @property
    def client(self):
        """Lazy initialization of boto3 client."""
        if self._client is None:
            self._client = boto3.client('secretsmanager')
        return self._client
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a specific secret value by key.
        First tries AWS Secrets Manager, then falls back to environment variables if configured.
        
        Args:
            key: The key of the secret to retrieve
            
        Returns:
            The secret value if found, None otherwise
        """
        try:
            # Try AWS Secrets Manager first
            if self._secret_name not in self._secrets_cache:
                response = self.client.get_secret_value(SecretId=self._secret_name)
                self._secrets_cache[self._secret_name] = json.loads(response['SecretString'])
            
            return self._secrets_cache[self._secret_name].get(key)
        except ClientError as e:
            logger.error(f"Failed to retrieve secret {key}: {str(e)}")
            
            # Fall back to environment variables if enabled
            if self._use_env_fallback:
                env_key = key.upper()
                if env_value := os.environ.get(env_key):
                    logger.info(f"Using environment variable fallback for {key}")
                    return env_value
            
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret {key}: {str(e)}")
            
            # Fall back to environment variables if enabled
            if self._use_env_fallback:
                env_key = key.upper()
                if env_value := os.environ.get(env_key):
                    logger.info(f"Using environment variable fallback for {key}")
                    return env_value
            
            return None
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from secrets or environment"""
        return self.get_secret('openai_api_key')
    
    def get_pinecone_api_key(self) -> Optional[str]:
        """Get Pinecone API key from secrets or environment"""
        return self.get_secret('pinecone_api_key')
    
    def get_openai_org_id(self) -> Optional[str]:
        """Get OpenAI organization ID from secrets or environment"""
        return self.get_secret('openai_org_id')
    
    def get_openai_base_url(self) -> str:
        """Get OpenAI base URL from secrets or environment"""
        return self.get_secret('openai_base_url') or "https://api.openai.com/v1"

    def get_pinecone_environment(self) -> str:
        """Get Pinecone environment from secrets or environment"""
        return self.get_secret('pinecone_environment') or "us-east-1"

    def get_pinecone_index_name(self) -> str:
        """Get Pinecone index name from secrets or environment"""
        return self.get_secret('pinecone_index_name') or "talk-embeddings" 