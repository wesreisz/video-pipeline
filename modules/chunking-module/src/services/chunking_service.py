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
            Dict: Dictionary containing the processed segments
        """
        logger.info(f"Processing transcription from s3://{bucket}/{key}")
        
        # Extract test_id from the key if present
        test_id = None
        if '_' in key:
            filename = os.path.basename(key)
            parts = filename.split('_')
            if len(parts) > 1:
                # Assume the last part before the extension is the test_id
                test_id = parts[-1].split('.')[0]
                logger.info(f"Detected test_id: {test_id}")
        
        # Load audio segments from the transcription file
        audio_segments = self.transcription_loader.get_audio_segments(bucket, key)
        
        # Convert audio segments to a dictionary for further processing
        segments_dict = self._convert_segments_to_dict(audio_segments)
        
        # Log detailed information about the segments instead of writing to a bucket
        self._log_segments_details(segments_dict, test_id)
        
        logger.info(f"Processed {len(audio_segments)} audio segments")
        
        return segments_dict
    
    def _log_segments_details(self, segments_dict: Dict[str, Any], test_id: str = None):
        """
        Log detailed information about the segments to CloudWatch.
        
        Args:
            segments_dict: Dictionary containing segmented data
            test_id: Optional test ID for filtering logs
        """
        segments_count = segments_dict.get("segments_count", 0)
        total_duration = segments_dict.get("total_duration", 0)
        
        # Log summary information
        logger.info(f"CHUNK PROCESSING SUMMARY - TestID: {test_id}")
        logger.info(f"CHUNK COUNT: {segments_count}")
        logger.info(f"CHUNK TOTAL DURATION: {total_duration:.2f} seconds")
        
        # Log information about each segment
        segments = segments_dict.get("segments", [])
        logger.info(f"CHUNK DETAILS - {segments_count} segments found:")
        
        for i, segment in enumerate(segments):
            # Convert string time values to float
            start_time = float(segment.get("start_time", 0)) if isinstance(segment.get("start_time"), str) else segment.get("start_time", 0)
            end_time = float(segment.get("end_time", 0)) if isinstance(segment.get("end_time"), str) else segment.get("end_time", 0)
            text = segment.get("text", segment.get("transcript", ""))
            confidence = segment.get("confidence", "N/A")
            
            logger.info(f"CHUNK[{i+1}]: {start_time:.2f}s - {end_time:.2f}s (Duration: {end_time-start_time:.2f}s)")
            logger.info(f"CHUNK[{i+1}] TEXT: \"{text}\"")
            logger.info(f"CHUNK[{i+1}] CONFIDENCE: {confidence}")
        
        # Log a marker for easy searching in CloudWatch
        logger.info(f"CHUNKING COMPLETE - TestID: {test_id}")
    
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
                float(segment.get("end_time", 0)) - float(segment.get("start_time", 0))
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
        
        # Log detailed information about the segments
        filename = os.path.basename(file_path)
        test_id = f"local-{filename.split('.')[0]}"
        self._log_segments_details(segments_dict, test_id)
        
        logger.info(f"Processed {len(audio_segments)} audio segments from local file")
        
        return segments_dict 