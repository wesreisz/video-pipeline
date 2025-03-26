import os
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

from openai import OpenAI, APITimeoutError, APIError
from utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class EmbeddingResponse:
    """Response model for embedding creation."""
    embedding: List[float]
    model: str
    usage: Dict[str, int]

class OpenAIServiceError(Exception):
    """Base exception for OpenAI service errors."""
    pass

class OpenAIService:
    """Service for interacting with OpenAI API to generate embeddings."""
    
    DEFAULT_MODEL = "text-embedding-ada-002"  # Base model name without version
    
    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize OpenAI service.
        
        Args:
            client: Optional OpenAI client for testing purposes
        """
        if client is not None:
            self.client = client
            logger.info("Using provided OpenAI client")
            return
            
        # Get required configuration
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise OpenAIServiceError("OpenAI API key not configured")
        
        # Get optional configuration
        timeout = float(os.environ.get('OPENAI_TIMEOUT', '20.0'))
        max_retries = int(os.environ.get('OPENAI_MAX_RETRIES', '3'))
        
        try:
            # Configure the client with settings
            client_kwargs = {
                "api_key": self.api_key,
                "timeout": timeout,
                "max_retries": max_retries
            }
            
            # Add optional configuration if environment variables are set
            if base_url := os.environ.get('OPENAI_BASE_URL'):
                client_kwargs['base_url'] = base_url
                logger.info("Using custom base URL: %s", base_url)
            
            if org_id := os.environ.get('OPENAI_ORG_ID'):
                client_kwargs['organization'] = org_id
                logger.info("Using organization ID: %s", org_id)
                
            self.client = OpenAI(**client_kwargs)
            logger.info("OpenAI client initialized with timeout=%s, max_retries=%s", 
                       timeout, max_retries)
            
        except Exception as e:
            logger.error("Failed to initialize OpenAI client: %s", str(e))
            raise OpenAIServiceError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def create_embedding(self, text: str, model: str = DEFAULT_MODEL) -> EmbeddingResponse:
        """
        Create embeddings for the given text using OpenAI's API.
        
        Args:
            text: The text to create embeddings for
            model: The model to use for embedding creation
            
        Returns:
            EmbeddingResponse containing the embedding vector and usage statistics
            
        Raises:
            OpenAIServiceError: If the API call fails or returns invalid response
        """
        if not text:
            raise OpenAIServiceError("Input text cannot be empty")
            
        logger.info("Creating embedding for text of length: %d using model: %s", 
                   len(text), model)
        
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            
            # Extract the first embedding (we only sent one text)
            embedding_data = response.data[0]
            
            # Get the actual model version from the response
            actual_model = getattr(response, 'model', model)
            
            return EmbeddingResponse(
                embedding=embedding_data.embedding,
                model=actual_model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except APITimeoutError as e:
            logger.error("OpenAI API timeout: %s", str(e))
            raise OpenAIServiceError(f"OpenAI API timeout: {str(e)}")
        except APIError as e:
            logger.error("OpenAI API error: %s", str(e))
            raise OpenAIServiceError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during embedding creation: %s", str(e))
            raise OpenAIServiceError(f"Unexpected error during embedding creation: {str(e)}") 