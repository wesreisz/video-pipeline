import json
import logging
import os
import tempfile
import boto3
import uuid
import time
from models.transcription_result import TranscriptionResult
from utils.s3_utils import S3Utils

logger = logging.getLogger()

class TranscriptionService:
    """Service to handle audio transcription logic using AWS Transcribe"""
    
    def __init__(self):
        self.s3_utils = S3Utils()
        self.output_bucket = os.environ.get('TRANSCRIPTION_OUTPUT_BUCKET')
        self.region = os.environ.get('TRANSCRIBE_REGION', 'us-east-1')
        self.transcribe_client = boto3.client('transcribe', region_name=self.region)
        
    def process_audio(self, bucket, key):
        """
        Process an audio file from S3 and generate transcription using AWS Transcribe
        
        Args:
            bucket (str): Source S3 bucket name
            key (str): S3 object key for the audio file
            
        Returns:
            str: The S3 key where the transcription was saved
        """
        logger.info(f"Starting transcription process for {key}")
        
        # Generate a unique job name for AWS Transcribe
        job_name = f"transcribe-{str(uuid.uuid4())}"
        file_uri = f"s3://{bucket}/{key}"
        
        # Start transcription job
        media_format = os.path.splitext(key)[1][1:].lower()  # Get file extension without dot
        if media_format == 'mp3':
            media_format = 'mp3'
        elif media_format in ['wav', 'wave']:
            media_format = 'wav'
        else:
            media_format = 'mp3'  # Default to mp3 if unknown
            
        logger.info(f"Starting AWS Transcribe job: {job_name} for {file_uri} with format {media_format}")
        
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
            transcription_text = self._wait_for_transcription(job_name)
            
            # Create result object with our standard format
            result = TranscriptionResult(
                original_file=key,
                transcription_text=transcription_text,
                timestamp=self.s3_utils.get_current_timestamp(),
                job_name=job_name
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
        Wait for an AWS Transcribe job to complete
        
        Args:
            job_name (str): The name of the transcription job
            max_attempts (int): Maximum number of polling attempts
            delay_seconds (int): Seconds to wait between polling attempts
            
        Returns:
            str: Transcribed text
        """
        logger.info(f"Waiting for transcription job {job_name} to complete")
        
        for attempt in range(max_attempts):
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if status == 'COMPLETED':
                logger.info(f"Transcription job {job_name} completed successfully")
                
                # Get transcript from the output file
                transcript_file_key = f"raw_transcriptions/{job_name}.json"
                transcript_json = self.s3_utils.download_json(self.output_bucket, transcript_file_key)
                
                # Extract transcript text from AWS Transcribe output format
                transcription_text = transcript_json.get('results', {}).get('transcripts', [{}])[0].get('transcript', '')
                return transcription_text
                
            elif status == 'FAILED':
                failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown reason')
                logger.error(f"Transcription job {job_name} failed: {failure_reason}")
                raise Exception(f"Transcription failed: {failure_reason}")
                
            logger.info(f"Transcription job status: {status}, waiting ({attempt+1}/{max_attempts})")
            time.sleep(delay_seconds)
            
        # If we've exhausted all attempts
        raise Exception(f"Transcription job {job_name} did not complete within the allotted time") 