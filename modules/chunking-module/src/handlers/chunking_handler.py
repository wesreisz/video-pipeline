import json
import logging
import os
# Change relative imports to absolute imports for Lambda compatibility
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.error_handler import handle_error
from services.chunking_service import ChunkingService
from utils.s3_utils import S3Utils

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main entry point for the chunking Lambda function.
    
    Args:
        event: AWS Lambda event object (contains S3 event details or Step Functions input)
        context: AWS Lambda context object
    
    Returns:
        dict: Response containing success/failure information
    """
    try:
        logger.info("Hello World from Chunking Module!")
        
        # Check if event is None and raise an exception if it is
        if event is None:
            raise ValueError("Event cannot be None")
            
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle both direct S3 events and Step Functions invocations
        records = event.get('Records', [])
        
        # If no records found, check if this is from EventBridge/Step Functions
        if not records and 'detail' in event:
            logger.info("Processing event from Step Functions")
            # Extract records from detail object if available
            records = event.get('detail', {}).get('records', [])
        
        if records:
            s3_event = records[0].get('s3', {})
            source_bucket = s3_event.get('bucket', {}).get('name')
            source_key = s3_event.get('object', {}).get('key')
            
            if source_bucket and source_key:
                logger.info(f"Processing file {source_key} from bucket {source_bucket}")
                
                # Initialize service
                chunking_service = ChunkingService()
                
                try:
                    # Process the transcription file - now returns a dict with segments
                    segments_dict = chunking_service.process_media(source_bucket, source_key)
                except FileNotFoundError as e:
                    logger.error(f"File not found error: {str(e)}")
                    logger.info("Attempting direct S3 access as a fallback...")
                    
                    # Try direct S3 access as a fallback
                    try:
                        # Initialize S3Utils
                        s3_utils = S3Utils()
                        
                        # Download the transcription JSON directly
                        transcription_data = s3_utils.download_json(source_bucket, source_key)
                        
                        # If successful, create a simplified segments dictionary
                        audio_segments = transcription_data.get('audio_segments', [])
                        
                        # Create a basic segments dictionary
                        segments_dict = {
                            "segments_count": len(audio_segments),
                            "segments": audio_segments,
                            "total_duration": sum(
                                float(segment.get("end_time", 0)) - float(segment.get("start_time", 0))
                                for segment in audio_segments
                            )
                        }
                        
                        logger.info(f"Successfully accessed transcription directly from S3: {len(audio_segments)} segments found")
                    except Exception as s3_error:
                        logger.error(f"Direct S3 access also failed: {str(s3_error)}")
                        raise e  # Re-raise the original error
                
                # Log a summary of what we processed
                logger.info(f"CHUNKING SUMMARY: Processed file {source_key} and found {segments_dict.get('segments_count', 0)} segments")
                logger.info("Chunking details are logged to CloudWatch instead of writing to a bucket")
                
                # Get RequestId for easier log searching
                request_id = "unknown"
                if context:
                    request_id = getattr(context, 'aws_request_id', 'unknown')
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Chunking completed successfully',
                        'source_bucket': source_bucket,
                        'source_file': source_key,
                        'segments_count': segments_dict.get('segments_count', 0),
                        'total_duration': segments_dict.get('total_duration', 0),
                        'log_request_id': request_id,
                        'note': 'Chunking details are logged to CloudWatch instead of writing to a bucket'
                    })
                }
        
        # If not processing a file, just return success
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Chunking module initialized successfully',
                'event_received': event
            })
        }
    
    except Exception as e:
        logger.error(f"Error in chunking handler: {str(e)}")
        return handle_error(e, "Error in chunking module") 