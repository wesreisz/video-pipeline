import json
import logging
import os
import tempfile
import boto3
import uuid
import time
from abc import ABC, abstractmethod
from models.transcription_result import TranscriptionResult
from utils.s3_utils import S3Utils

logger = logging.getLogger()

class TranscriptionStrategy(ABC):
    """Abstract base class for transcription strategies"""
    
    @abstractmethod
    def process_transcription(self, job_name, output_bucket, s3_utils):
        """
        Process a completed transcription job and extract results
        
        Args:
            job_name (str): The transcription job name
            output_bucket (str): The S3 bucket containing transcription output
            s3_utils (S3Utils): Utility for S3 operations
            
        Returns:
            tuple: (transcription_text, word_segments, audio_segments)
        """
        pass

class AWSTranscribeStrategy(TranscriptionStrategy):
    """Strategy for processing AWS Transcribe output"""
    
    def process_transcription(self, job_name, output_bucket, s3_utils):
        """
        Process AWS Transcribe output and extract transcription data
        
        Args:
            job_name (str): The AWS Transcribe job name
            output_bucket (str): The S3 bucket containing transcription output
            s3_utils (S3Utils): Utility for S3 operations
            
        Returns:
            tuple: (transcription_text, word_segments, audio_segments)
        """
        logger.info(f"Processing transcription results for job {job_name}")
        
        # Get transcript from the output file
        transcript_file_key = f"raw_transcriptions/{job_name}.json"
        transcript_json = s3_utils.download_json(output_bucket, transcript_file_key)
        
        # Extract transcript text from AWS Transcribe output format
        results = transcript_json.get('results', {})
        transcription_text = results.get('transcripts', [{}])[0].get('transcript', '')
        
        # Extract word-level segments (items) with timestamps
        segments = results.get('items', [])
        
        # Extract sentence-level audio segments if available
        audio_segments = results.get('audio_segments', [])
        
        # Process word-level segments if exists
        processed_segments = []
        if segments:
            logger.info(f"Extracted {len(segments)} word-level segments from transcription")
            
            # We're only keeping the essential information from each segment
            for segment in segments:
                if segment.get('type') in ['pronunciation', 'punctuation']:
                    processed_segment = {
                        'type': segment.get('type'),
                        'content': segment.get('alternatives', [{}])[0].get('content', ''),
                        'start_time': segment.get('start_time'),
                        'end_time': segment.get('end_time'),
                        'confidence': segment.get('alternatives', [{}])[0].get('confidence', '0')
                    }
                    processed_segments.append(processed_segment)
            
            logger.info(f"Processed {len(processed_segments)} word-level segments")
        
        # Process sentence-level audio segments if exists
        processed_audio_segments = []
        if audio_segments:
            logger.info(f"Extracted {len(audio_segments)} sentence-level audio segments from transcription")
            
            # Process each sentence-level segment
            for segment in audio_segments:
                processed_audio_segment = {
                    'id': segment.get('id'),
                    'transcript': segment.get('transcript', ''),
                    'start_time': segment.get('start_time'),
                    'end_time': segment.get('end_time'),
                    'items': segment.get('items', [])
                }
                processed_audio_segments.append(processed_audio_segment)
            
            logger.info(f"Processed {len(processed_audio_segments)} sentence-level audio segments")
        
        # Return both transcription text and processed segments
        return transcription_text, processed_segments, processed_audio_segments


class TranscriptionStrategyFactory:
    """Factory for creating transcription strategies"""
    
    @staticmethod
    def create_strategy(provider='aws'):
        """
        Create a transcription strategy based on provider
        
        Args:
            provider (str): The transcription provider ('aws', etc.)
            
        Returns:
            TranscriptionStrategy: Strategy instance for the provider
        """
        if provider.lower() == 'aws':
            return AWSTranscribeStrategy()
        else:
            logger.warning(f"Unknown provider '{provider}', defaulting to AWS")
            return AWSTranscribeStrategy()


class TranscriptionService:
    """Service to handle audio and video transcription logic using AWS Transcribe"""
    
    def __init__(self, strategy_provider='aws'):
        self.s3_utils = S3Utils()
        self.output_bucket = os.environ.get('TRANSCRIPTION_OUTPUT_BUCKET')
        self.region = os.environ.get('TRANSCRIBE_REGION', 'us-east-1')
        self.transcribe_client = boto3.client('transcribe', region_name=self.region)
        self.strategy = TranscriptionStrategyFactory.create_strategy(strategy_provider)
        
    def set_strategy(self, strategy):
        """
        Set the transcription strategy
        
        Args:
            strategy (TranscriptionStrategy): The strategy to use
        """
        self.strategy = strategy
        
    def process_media(self, bucket, key):
        """
        Process an audio or video file from S3 and generate transcription using AWS Transcribe
        
        Args:
            bucket (str): Source S3 bucket name
            key (str): S3 object key for the audio or video file
            
        Returns:
            str: The S3 key where the transcription was saved
        """
        logger.info(f"Starting transcription process for {key}")
        
        # Generate a unique job name for AWS Transcribe
        job_name = f"transcribe-{str(uuid.uuid4())}"
        file_uri = f"s3://{bucket}/{key}"
        
        # Determine if the file is audio or video based on extension
        extension = os.path.splitext(key)[1][1:].lower()
        
        # Set media format and type based on file extension
        media_format = extension
        
        # Determine if it's audio or video based on the extension
        if extension in ['mp3', 'wav', 'flac', 'ogg', 'amr']:
            media_type = 'audio'
        elif extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            media_type = 'video'
        else:
            logger.warning(f"Unsupported file extension: {extension}, defaulting to audio")
            media_type = 'audio'
            
        logger.info(f"Processing {media_type} file in {media_format} format")
        
        try:
            # Start the transcription job
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': file_uri},
                MediaFormat=media_format,
                LanguageCode='en-US',  # Default to English, could be parameterized
                OutputBucketName=self.output_bucket,
                OutputKey=f"raw_transcriptions/{job_name}.json"
            )
            
            # Wait for transcription job to complete
            transcription_text, segments, audio_segments = self._wait_for_transcription(job_name)
            
            # Create result object with our standard format
            result = TranscriptionResult(
                original_file=key,
                transcription_text=transcription_text,
                timestamp=self.s3_utils.get_current_timestamp(),
                job_name=job_name,
                media_type=media_type,
                segments=segments,
                audio_segments=audio_segments
            )
            
            # Save result to S3 in our standard format
            output_key = f"transcriptions/{os.path.splitext(os.path.basename(key))[0]}.json"
            self.s3_utils.upload_json(self.output_bucket, output_key, result.to_dict())
            
            logger.info(f"Transcription complete. Result saved to {self.output_bucket}/{output_key}")
            return output_key
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise
    
    def _wait_for_transcription(self, job_name, max_attempts=30, delay_seconds=10):
        """
        Wait for AWS Transcribe job to complete and retrieve the result
        
        Args:
            job_name (str): The AWS Transcribe job name to wait for
            max_attempts (int, optional): Maximum number of attempts before giving up
            delay_seconds (int, optional): Delay between status check attempts in seconds
            
        Returns:
            tuple: The transcription text and processed segments
            
        Raises:
            Exception: If the transcription job fails or times out
        """
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            logger.info(f"Transcription job {job_name} status: {status} (attempt {attempt}/{max_attempts})")
            
            if status == 'COMPLETED':
                logger.info(f"Transcription job {job_name} completed successfully")
                
                # Use the selected strategy to process the transcription result
                return self.strategy.process_transcription(job_name, self.output_bucket, self.s3_utils)
            
            elif status == 'FAILED':
                error_message = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
                logger.error(f"Transcription job {job_name} failed: {error_message}")
                raise Exception(f"Transcription job failed: {error_message}")
            
            # Sleep before the next attempt
            time.sleep(delay_seconds)
        
        # If max attempts reached without completion
        logger.error(f"Transcription job {job_name} did not complete within {max_attempts} attempts")
        raise Exception(f"Transcription job timed out after {max_attempts} attempts") 