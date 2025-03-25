import os
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

import openai
from openai import OpenAI
from ..utils.logger import setup_logger

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
            
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise OpenAIServiceError("OpenAI API key not configured")
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenAI client: %s", str(e))
            raise OpenAIServiceError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def create_embedding(self, text: str, model: str = "text-embedding-ada-002") -> EmbeddingResponse:
        """
        Create embeddings for the given text using OpenAI's API.
        
        Args:
            text: The text to create embeddings for
            model: The model to use for embedding creation (default: text-embedding-ada-002)
            
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
            
            return EmbeddingResponse(
                embedding=embedding_data.embedding,
                model=model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except openai.APIError as e:
            logger.error("OpenAI API error: %s", str(e))
            raise OpenAIServiceError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error during embedding creation: %s", str(e))
            raise OpenAIServiceError(f"Unexpected error during embedding creation: {str(e)}") 