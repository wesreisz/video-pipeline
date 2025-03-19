import logging
import os
import sys
import json
from typing import List, Dict, Any

# Try different import approaches
try:
    # Relative import within the module
    from .transcription_loader_service import TranscriptionLoaderService
    from ..models.chunk import Chunk, ChunkingResult
except ImportError:
    try:
        # Absolute import within the module
        from src.services.transcription_loader_service import TranscriptionLoaderService
        from src.models.chunk import Chunk, ChunkingResult
    except ImportError:
        print("WARNING: Failed to import required modules")

logger = logging.getLogger()

class ChunkingService:
    """
    Service for chunking media files into segments.
    """
    
    def __init__(self, region=None):
        """
        Initialize the chunking service.
        
        Args:
            region: AWS region (optional)
        """
        logger.info("Initializing Chunking Service")
        self.transcription_loader = TranscriptionLoaderService(region)
        
    def process_media(self, bucket, key):
        """
        Process a transcription file and break it into chunks.
        
        Args:
            bucket: S3 bucket containing the transcription file
            key: S3 key for the transcription file
            
        Returns:
            str: Output key where the chunking results are stored
        """
        logger.info(f"Processing transcription from s3://{bucket}/{key}")
        
        # Load audio segments from the transcription file
        audio_segments = self.transcription_loader.get_audio_segments(bucket, key)
        
        # Convert audio segments to a dictionary for further processing
        segments_dict = self._convert_segments_to_dict(audio_segments)
        
        logger.info(f"Processed {len(audio_segments)} audio segments")
        
        # You can add additional processing here if needed
        
        return segments_dict
    
    def _convert_segments_to_dict(self, audio_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert a list of audio segments to a dictionary format.
        
        Args:
            audio_segments: List of audio segments from the transcription
            
        Returns:
            Dict[str, Any]: Dictionary containing segmented data
        """
        result = {
            "segments_count": len(audio_segments),
            "segments": audio_segments
        }
        
        # Extract additional metadata if needed
        if audio_segments:
            result["total_duration"] = sum(
                segment.get("end_time", 0) - segment.get("start_time", 0) 
                for segment in audio_segments
            )
            
        return result
        
    def process_local_file(self, file_path):
        """
        Process a local transcription file for testing or development.
        
        Args:
            file_path: Path to the local transcription file
            
        Returns:
            Dict: Dictionary containing the processed audio segments
        """
        logger.info(f"Processing local transcription file: {file_path}")
        
        # Load audio segments from the local file
        audio_segments = self.transcription_loader.get_audio_segments_from_file(file_path)
        
        # Convert audio segments to a dictionary
        segments_dict = self._convert_segments_to_dict(audio_segments)
        
        logger.info(f"Processed {len(audio_segments)} audio segments from local file")
        
        return segments_dict 