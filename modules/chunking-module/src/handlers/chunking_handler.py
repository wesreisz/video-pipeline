import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional, TypedDict, Tuple
import boto3
from botocore.exceptions import ClientError
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

def extract_s3_details(event: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    """
    Extract S3 bucket and key from event records.
    
    Args:
        event: Event containing S3 details in EventBridge format
        
    Returns:
        tuple: (bucket_name, object_key) if found, None otherwise
    """
    # Check for EventBridge format
    if 'detail' in event:
        records = event.get('detail', {}).get('records', [])
        if records:
            s3_event = records[0].get('s3', {})
            bucket = s3_event.get('bucket', {}).get('name')
            key = s3_event.get('object', {}).get('key')
            
            if bucket and key:
                return (bucket, key)
    
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

def send_to_sqs(audio_segments: List[AudioSegment], queue_url: Optional[str] = None) -> int:
    """
    Send audio segments to SQS queue.
    
    Args:
        audio_segments: List of audio segments to send
        queue_url: Optional queue URL, if not provided will be fetched from environment
        
    Returns:
        Number of segments sent successfully
    """
    sqs_client = boto3.client('sqs')
    sent_count = 0
    queue_url = queue_url or get_sqs_queue_url()
    
    for segment in audio_segments:
        try:
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(segment)
            )
            sent_count += 1
            logger.info(f"Sent segment to SQS: MessageId={response['MessageId']}")
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
        
        source_bucket, source_key = s3_details
        logger.info(f"Processing file {source_key} from bucket {source_bucket}")
        
        json_data = get_s3_object(source_bucket, source_key)
        audio_segments = process_audio_segments(json_data)

        # Send audio segments to SQS
        sent_count = send_to_sqs(audio_segments)
        
        response_data = {
            'message': 'Chunking completed successfully',
            'segments_sent': sent_count,
            'source_bucket': source_bucket,
            'source_file': source_key,
            'note': 'Audio segments have been sent to SQS queue'
        }
        
        return {
            'statusCode': SUCCESS_STATUS_CODE,
            'body': json.dumps(response_data)
        }
    
    except Exception as e:
        logger.error(f"Error in chunking handler: {str(e)}")
        return handle_error(e, ERROR_MESSAGE_PREFIX) 