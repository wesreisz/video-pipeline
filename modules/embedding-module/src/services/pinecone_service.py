import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import pinecone
from pinecone import Pinecone, ServerlessSpec, CloudProvider

from utils.logger import get_logger
from services.secrets_service import SecretsService

logger = get_logger(__name__)

@dataclass
class UpsertResponse:
    """Response model for upsert operation."""
    upserted_count: int
    namespace: Optional[str] = None
    total_vector_count: Optional[int] = None

@dataclass
class TalkMetadata:
    """Metadata model for talk segments."""
    speaker: List[str]
    start_time: str
    end_time: str
    title: str
    track: str
    day: str
    text: str
    original_file: str = ""  # Path to the original media file
    segment_id: str = ""     # Original segment ID from transcription

class PineconeServiceError(Exception):
    """Base exception for Pinecone service errors."""
    pass

class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    DEFAULT_ENVIRONMENT = "us-east-1"
    DEFAULT_INDEX_NAME = "talk-embeddings"
    DIMENSION = 1536  # OpenAI embedding dimension
    
    def __init__(self, secrets_service: Optional[SecretsService] = None):
        """
        Initialize Pinecone service.
        
        Args:
            secrets_service: Optional SecretsService for testing purposes
        """
        try:
            # Initialize secrets service
            self.secrets_service = secrets_service or SecretsService()
            
            # Get required configuration
            self.api_key = self.secrets_service.get_pinecone_api_key()
            if not self.api_key:
                logger.error("Pinecone API key not found in secrets")
                raise PineconeServiceError("Pinecone API key not configured")
            
            # Get optional configuration with defaults
            self.environment = self.secrets_service.get_pinecone_environment() or self.DEFAULT_ENVIRONMENT
            self.index_name = self.secrets_service.get_pinecone_index_name() or self.DEFAULT_INDEX_NAME
            
            # Initialize Pinecone client with v6.0.2 API
            self.pinecone = Pinecone(api_key=self.api_key)
            logger.info("Pinecone client initialized")
            
            # Ensure index exists
            self._ensure_index_exists()
            
            # Get index instance
            self.index = self.pinecone.Index(self.index_name)
            logger.info("Connected to Pinecone index: %s", self.index_name)
            
            # Verify initial storage status
            self._verify_storage_status()
            
        except Exception as e:
            logger.error("Failed to initialize Pinecone service: %s", str(e))
            raise PineconeServiceError(f"Failed to initialize Pinecone service: {str(e)}")
    
    def _verify_storage_status(self) -> Dict[str, Any]:
        """
        Verify storage status by checking index statistics.
        
        Returns:
            Dict containing index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            total_vector_count = stats.total_vector_count
            dimension = stats.dimension
            
            logger.info(
                "Index status - Total vectors: %d, Dimension: %d",
                total_vector_count,
                dimension
            )
            
            if dimension != self.DIMENSION:
                raise PineconeServiceError(
                    f"Index dimension mismatch. Expected {self.DIMENSION}, got {dimension}"
                )
            
            return stats
            
        except Exception as e:
            logger.error("Error verifying storage status: %s", str(e))
            raise PineconeServiceError(f"Error verifying storage status: {str(e)}")
    
    def _ensure_index_exists(self) -> None:
        """
        Ensure the required index exists with correct configuration.
        Checks if the index exists and verifies its configuration.
        """
        try:
            # Check if index already exists
            existing_indexes = [index.name for index in self.pinecone.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info("Creating new Pinecone index: %s", self.index_name)
                try:
                    # Create index with required configuration using v6.0.2 API
                    self.pinecone.create_index(
                        name=self.index_name,
                        dimension=self.DIMENSION,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud=CloudProvider.AWS,
                            region=self.environment
                        )
                    )
                    logger.info("Successfully created Pinecone index")
                except Exception as create_error:
                    if "already exists" in str(create_error).lower():
                        logger.info("Index was created by another process: %s", self.index_name)
                    else:
                        raise create_error
            else:
                logger.info("Pinecone index already exists: %s", self.index_name)
                
        except Exception as e:
            logger.error("Error ensuring index exists: %s", str(e))
            raise PineconeServiceError(f"Error ensuring index exists: {str(e)}")
    
    def upsert_embeddings(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[TalkMetadata],
        namespace: Optional[str] = None
    ) -> UpsertResponse:
        """
        Upsert vectors with metadata to Pinecone.
        
        Args:
            vectors: List of embedding vectors
            ids: List of vector IDs
            metadata: List of TalkMetadata objects
            namespace: Optional namespace for the vectors
            
        Returns:
            UpsertResponse containing the number of vectors upserted
            
        Raises:
            PineconeServiceError: If the upsert operation fails
        """
        try:
            if not vectors or not ids or not metadata:
                raise ValueError("Vectors, IDs, and metadata lists cannot be empty")
            
            if len(vectors) != len(ids) or len(vectors) != len(metadata):
                raise ValueError("Vectors, IDs, and metadata lists must have the same length")
            
            # Prepare vectors with metadata
            vector_data = []
            for vec, id_, meta in zip(vectors, ids, metadata):
                # Convert metadata to dict
                meta_dict = {
                    "speaker": meta.speaker,
                    "start_time": meta.start_time,
                    "end_time": meta.end_time,
                    "title": meta.title,
                    "track": meta.track,
                    "day": meta.day,
                    "text": meta.text,
                    "original_file": meta.original_file,
                    "segment_id": meta.segment_id
                }
                
                vector_data.append((id_, vec, meta_dict))
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=vector_data,
                namespace=namespace
            )
            
            # Verify storage status after upsert
            stats = self._verify_storage_status()
            
            logger.info(
                "Successfully upserted %d vectors to namespace %s",
                len(vector_data),
                namespace or "default"
            )
            
            return UpsertResponse(
                upserted_count=len(vector_data),
                namespace=namespace,
                total_vector_count=stats.total_vector_count
            )
            
        except ValueError as e:
            logger.error("Invalid input for upsert operation: %s", str(e))
            raise PineconeServiceError(f"Invalid input for upsert operation: {str(e)}")
        except Exception as e:
            logger.error("Error upserting vectors: %s", str(e))
            raise PineconeServiceError(f"Error upserting vectors: {str(e)}") 