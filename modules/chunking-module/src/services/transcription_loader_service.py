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
                
                def download_json(self, bucket, key):
                    return {}

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
        
        # Try using the direct JSON download method first, which is more reliable
        try:
            logger.info(f"Attempting direct JSON download from S3: {bucket}/{key}")
            transcription_data = self.s3_utils.download_json(bucket, key)
            logger.info(f"Successfully loaded transcription JSON directly from S3")
        except Exception as e:
            logger.warning(f"Direct JSON download failed, falling back to file download: {str(e)}")
            
            # Create a temporary directory for downloads if it doesn't exist
            temp_dir = "/tmp/transcriptions"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate a local filename from the S3 key
            filename = os.path.basename(key)
            local_path = os.path.join(temp_dir, filename)
            
            try:
                # Download the file
                self.s3_utils.download_file(bucket, key, local_path)
                
                # Read and parse the JSON file
                with open(local_path, 'r') as file:
                    transcription_data = json.loads(file.read())
                    
                logger.info(f"Successfully loaded transcription from local file: {local_path}")
            except Exception as e:
                logger.error(f"Both direct and file-based S3 downloads failed: {str(e)}")
                logger.info("Attempting emergency S3 API direct access as last resort")
                
                # Last resort: Try to use boto3 directly
                try:
                    import boto3
                    s3_client = boto3.client('s3')
                    response = s3_client.get_object(Bucket=bucket, Key=key)
                    content = response['Body'].read().decode('utf-8')
                    transcription_data = json.loads(content)
                    logger.info("Emergency direct S3 access succeeded")
                except Exception as e2:
                    logger.error(f"All S3 access methods failed: {str(e2)}")
                    raise ValueError(f"Cannot load transcription from S3: {bucket}/{key}. Error: {str(e)}")
        
        # Log details about what we found
        audio_segments = transcription_data.get('audio_segments', [])
        segments = transcription_data.get('segments', [])
        transcript_text = transcription_data.get('transcription_text', '')
        
        logger.info(f"Successfully loaded transcription for {transcription_data.get('original_file', key)}")
        logger.info(f"Transcript length: {len(transcript_text)} characters")
        logger.info(f"Found {len(segments)} word-level segments")
        logger.info(f"Found {len(audio_segments)} audio segments")
            
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
        
        # First try to get standard audio_segments
        audio_segments = transcription_data.get('audio_segments', [])
        
        # If no audio_segments, but we have word-level segments, try to convert those
        if not audio_segments and 'segments' in transcription_data:
            logger.info("No audio_segments found, trying to use word-level segments")
            audio_segments = self._convert_word_segments_to_audio_segments(transcription_data.get('segments', []))
            
        # If still no segments but we have transcription text, create a single segment
        if not audio_segments and 'transcription_text' in transcription_data:
            logger.info("No segments found, creating a single segment from transcription text")
            audio_segments = [{
                'start_time': 0.0,
                'end_time': 60.0,  # Assume 1 minute if we don't know
                'text': transcription_data.get('transcription_text', ''),
                'transcript': transcription_data.get('transcription_text', ''),
                'confidence': 1.0
            }]
            
        logger.info(f"Returning {len(audio_segments)} audio segments for processing")
        return audio_segments
    
    def _convert_word_segments_to_audio_segments(self, word_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert word-level segments to audio segments by grouping them.
        
        Args:
            word_segments: List of word-level segments
            
        Returns:
            List[Dict[str, Any]]: List of audio segments
        """
        if not word_segments:
            return []
            
        # Sort segments by start_time if available
        try:
            word_segments = sorted(word_segments, key=lambda x: float(x.get('start_time', 0)))
        except (ValueError, TypeError):
            logger.warning("Could not sort word segments by start_time")
            
        # Group segments into audio segments (simplified approach: groups of 5-10 words)
        audio_segments = []
        current_segment = []
        current_text = []
        
        for word in word_segments:
            current_segment.append(word)
            word_text = word.get('text', word.get('content', ''))
            current_text.append(word_text)
            
            # Create a new segment every 5-10 words or at punctuation
            if len(current_segment) >= 10 or word_text.endswith(('.', '!', '?')):
                if current_segment:
                    start_time = float(current_segment[0].get('start_time', 0))
                    end_time = float(current_segment[-1].get('end_time', 0))
                    text = ' '.join(current_text)
                    
                    audio_segments.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': text,
                        'transcript': text,
                        'confidence': sum(float(word.get('confidence', 1.0)) for word in current_segment) / len(current_segment) if current_segment else 1.0
                    })
                    
                    current_segment = []
                    current_text = []
        
        # Add any remaining words
        if current_segment:
            start_time = float(current_segment[0].get('start_time', 0))
            end_time = float(current_segment[-1].get('end_time', 0))
            text = ' '.join(current_text)
            
            audio_segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'text': text,
                'transcript': text,
                'confidence': sum(float(word.get('confidence', 1.0)) for word in current_segment) / len(current_segment) if current_segment else 1.0
            })
            
        logger.info(f"Converted {len(word_segments)} word segments into {len(audio_segments)} audio segments")
        return audio_segments
        
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
        
        try:
            with open(file_path, 'r') as file:
                transcription_data = json.load(file)
        except Exception as e:
            logger.error(f"Error loading transcription from file {file_path}: {str(e)}")
            raise
        
        # Log details about what we found
        audio_segments = transcription_data.get('audio_segments', [])
        segments = transcription_data.get('segments', [])
        transcript_text = transcription_data.get('transcription_text', '')
        
        logger.info(f"Successfully loaded transcription for {transcription_data.get('original_file', file_path)}")
        logger.info(f"Transcript length: {len(transcript_text)} characters")
        logger.info(f"Found {len(segments)} word-level segments")
        logger.info(f"Found {len(audio_segments)} audio segments")
            
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
        
        # First try to get standard audio_segments
        audio_segments = transcription_data.get('audio_segments', [])
        
        # If no audio_segments, but we have word-level segments, try to convert those
        if not audio_segments and 'segments' in transcription_data:
            logger.info("No audio_segments found, trying to use word-level segments")
            audio_segments = self._convert_word_segments_to_audio_segments(transcription_data.get('segments', []))
            
        # If still no segments but we have transcription text, create a single segment
        if not audio_segments and 'transcription_text' in transcription_data:
            logger.info("No segments found, creating a single segment from transcription text")
            audio_segments = [{
                'start_time': 0.0,
                'end_time': 60.0,  # Assume 1 minute if we don't know
                'text': transcription_data.get('transcription_text', ''),
                'transcript': transcription_data.get('transcription_text', ''),
                'confidence': 1.0
            }]
            
        logger.info(f"Returning {len(audio_segments)} audio segments for processing")
        return audio_segments 