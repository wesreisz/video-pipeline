import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional, TypedDict, Tuple
import boto3
from botocore.exceptions import ClientError
import random
import string
import hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_handler import handle_error

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
SUCCESS_STATUS_CODE = 200
ERROR_MESSAGE_PREFIX = "Error in chunking module"

class S3EventDetail(TypedDict):
    bucket: Dict[str, str]
    object: Dict[str, str]

class AudioSegment(TypedDict):
    start_time: float
    end_time: float
    text: str

def get_sqs_queue_url() -> str:
    """Get the SQS queue URL from environment variables."""
    queue_url = os.environ.get('SQS_QUEUE_URL')
    if not queue_url:
        raise ValueError("SQS_QUEUE_URL environment variable is not set")
    return queue_url

def extract_s3_details(event: Dict[str, Any]) -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """
    Extract S3 bucket, key and metadata from event records.
    
    Args:
        event: Event containing S3 details in EventBridge format
        
    Returns:
        tuple: (bucket_name, object_key, metadata) if found, None otherwise
    """
    # Check for EventBridge format
    if 'detail' in event:
        records = event.get('detail', {}).get('records', [])
        if records:
            record = records[0]
            s3_event = record.get('s3', {})
            bucket = s3_event.get('bucket', {}).get('name')
            key = s3_event.get('object', {}).get('key')
            metadata = record.get('metadata', {})
            
            if bucket and key:
                return (bucket, key, metadata)
    
    return None

def process_audio_segments(json_data: Dict[str, Any]) -> List[AudioSegment]:
    """
    Process audio segments from JSON data.
    
    Args:
        json_data: Parsed JSON data containing audio segments
        
    Returns:
        List of audio segments
    """
    # Try to get audio segments from the new format first
    audio_segments = json_data.get('audio_segments', [])
    
    if not audio_segments:
        # Fallback to old format
        audio_segments = json_data.get('results', {}).get('segments', [])
    
    if not audio_segments:
        logger.warning("No audio segments found in the data")
    else:
        logger.info(f"Successfully loaded {len(audio_segments)} audio segments")
        if audio_segments:
            logger.debug(
                f"First segment starts at {audio_segments[0].get('start_time')} "
                f"and ends at {audio_segments[0].get('end_time')}"
            )
    
    return audio_segments

def get_s3_object(bucket: str, key: str) -> Dict[str, Any]:
    """
    Retrieve and parse JSON object from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        Parsed JSON data
    
    Raises:
        ValueError: If object doesn't exist or isn't valid JSON
        ClientError: If S3 operation fails
    """
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise ValueError(f"File {key} not found in bucket {bucket}")
        raise
    except json.JSONDecodeError:
        raise ValueError(f"File {key} is not valid JSON")

def generate_chunk_hash(original_file: str, segment_id: int) -> str:
    """
    Generate a deterministic hash from original file name and segment ID.
    Returns only the first 10 characters of the hash for brevity.
    
    Args:
        original_file: Path to the original media file
        segment_id: ID of the segment within the file
        
    Returns:
        A 10-character hexadecimal hash string
        
    Raises:
        ValueError: If inputs are invalid (None, empty string, or negative segment_id)
    """
    # Validate inputs
    if not original_file:
        raise ValueError("original_file cannot be empty or None")
    if segment_id is None or segment_id < 0:
        raise ValueError("segment_id must be a non-negative integer")
        
    # Create a unique string combining the file path and segment ID
    unique_string = f"{original_file}:{segment_id}"
    
    # Generate SHA-256 hash and return first 10 characters
    hash_object = hashlib.sha256(unique_string.encode('utf-8'))
    return hash_object.hexdigest()[:10]

def send_to_sqs(audio_segments: List[AudioSegment], original_file: str, metadata: Dict[str, Any], queue_url: Optional[str] = None) -> int:
    """
    Send audio segments to SQS queue.
    
    Args:
        audio_segments: List of audio segments to send
        original_file: Name of the original processed file
        metadata: Metadata associated with the original file
        queue_url: Optional queue URL, if not provided will be fetched from environment
        
    Returns:
        Number of segments sent successfully
    """
    sqs_client = boto3.client('sqs')
    sent_count = 0
    queue_url = queue_url or get_sqs_queue_url()
    
    for segment in audio_segments:
        try:
            # Get text content from either 'text' or 'transcript' field
            text_content = segment.get('text', segment.get('transcript', ''))
            
            # Generate unique chunk_id using hash
            chunk_id = generate_chunk_hash(original_file, segment['id'])
            
            # Create message with unique chunk_id and metadata
            message = {
                'chunk_id': chunk_id,
                'text': text_content,
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'original_file': original_file,
                'segment_id': segment['id'],  # Keep original segment ID for reference
                'metadata': metadata  # Include the metadata
            }
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message)
            )
            sent_count += 1
            logger.info(f"Sent segment to SQS: MessageId={response['MessageId']}, ChunkId={chunk_id}, Metadata={metadata}")
        except Exception as e:
            logger.error(f"Failed to send segment to SQS: {str(e)}")
            raise
    
    return sent_count

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entry point for the chunking Lambda function.
    
    Args:
        event: AWS Lambda event object (contains S3 event details or Step Functions input)
        context: AWS Lambda context object
    
    Returns:
        dict: Response containing success/failure information
    """
    try:
        logger.info("Inside the Chunking Module!")
        
        if event is None:
            raise ValueError("Event cannot be None")
            
        logger.info(f"Received event: {json.dumps(event)}")
        
        s3_details = extract_s3_details(event)
        if not s3_details:
            return {
                'statusCode': SUCCESS_STATUS_CODE,
                'body': json.dumps({
                    'message': 'No records to process',
                    'note': 'Event contained no records to process'
                })
            }
        
        source_bucket, source_key, metadata = s3_details
        logger.info(f"Processing file {source_key} from bucket {source_bucket} with metadata: {metadata}")
        
        json_data = get_s3_object(source_bucket, source_key)
        audio_segments = process_audio_segments(json_data)

        # Send audio segments to SQS
        original_file = json_data.get('original_file')
        if not original_file:
            logger.warning("No original_file found in JSON data")
            original_file = source_key
            
        sent_count = send_to_sqs(audio_segments, original_file, metadata)
        
        response_data = {
            'message': 'Chunking completed successfully',
            'segments_sent': sent_count,
            'source_bucket': source_bucket,
            'source_file': source_key,
            'metadata': metadata,
            'note': 'Audio segments have been sent to SQS queue'
        }
        
        return {
            'statusCode': SUCCESS_STATUS_CODE,
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        logger.error(f"Error in chunking handler: {str(e)}")
        return handle_error(e, ERROR_MESSAGE_PREFIX) 