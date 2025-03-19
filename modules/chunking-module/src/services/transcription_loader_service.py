import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional

# Try different import approaches to handle various execution contexts
try:
    # First try relative import within module
    from ..utils.s3_utils import S3Utils
except ImportError:
    try:
        # Try absolute import within module
        from src.utils.s3_utils import S3Utils
    except ImportError:
        try:
            # Try import from shared_libs (with underscore)
            # Add parent directory to path if needed
            module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            if module_path not in sys.path:
                sys.path.append(module_path)
            from modules.shared_libs.utils import S3Utils
        except ImportError:
            print("WARNING: Cannot import S3Utils. Using placeholder implementation.")
            # Use placeholder if all imports fail
            class S3Utils:
                def __init__(self, region=None):
                    pass
                
                def download_file(self, bucket, key, local_path):
                    pass
                
                def upload_file(self, local_path, bucket, key):
                    pass
                
                def upload_json(self, data, bucket, key):
                    pass

logger = logging.getLogger()

class TranscriptionLoaderService:
    """
    Service for loading transcription results from the transcribe-module.
    """
    
    def __init__(self, region=None):
        """
        Initialize the transcription loader service.
        
        Args:
            region: AWS region (optional)
        """
        self.s3_utils = S3Utils(region)
        logger.info("Initialized TranscriptionLoaderService")
        
    def load_transcription_from_s3(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Load a transcription result from S3 and return its contents as a dictionary.
        
        Args:
            bucket: S3 bucket containing the transcription file
            key: S3 key for the transcription file
            
        Returns:
            Dict[str, Any]: Dictionary containing the transcription data
        """
        logger.info(f"Loading transcription from s3://{bucket}/{key}")
        
        # Create a temporary directory for downloads if it doesn't exist
        temp_dir = "/tmp/transcriptions"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a local filename from the S3 key
        filename = os.path.basename(key)
        local_path = os.path.join(temp_dir, filename)
        
        # Download the file
        self.s3_utils.download_file(bucket, key, local_path)
        
        # Read and parse the JSON file
        with open(local_path, 'r') as file:
            transcription_data = json.load(file)
            
        logger.info(f"Successfully loaded transcription data with {len(transcription_data.get('audio_segments', []))} audio segments")
        return transcription_data
    
    def get_audio_segments(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        """
        Extract audio segments from a transcription result.
        
        Args:
            bucket: S3 bucket containing the transcription file
            key: S3 key for the transcription file
            
        Returns:
            List[Dict[str, Any]]: List of audio segments from the transcription
        """
        transcription_data = self.load_transcription_from_s3(bucket, key)
        return transcription_data.get('audio_segments', [])
        
    def load_transcription_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load a transcription result from a local file.
        Useful for testing or local development.
        
        Args:
            file_path: Path to the transcription JSON file
            
        Returns:
            Dict[str, Any]: Dictionary containing the transcription data
        """
        logger.info(f"Loading transcription from local file: {file_path}")
        
        with open(file_path, 'r') as file:
            transcription_data = json.load(file)
            
        logger.info(f"Successfully loaded transcription data with {len(transcription_data.get('audio_segments', []))} audio segments")
        return transcription_data
    
    def get_audio_segments_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract audio segments from a local transcription file.
        Useful for testing or local development.
        
        Args:
            file_path: Path to the transcription JSON file
            
        Returns:
            List[Dict[str, Any]]: List of audio segments from the transcription
        """
        transcription_data = self.load_transcription_from_file(file_path)
        return transcription_data.get('audio_segments', []) 