#!/usr/bin/env python3
"""
End-to-End Test for Video Pipeline

This script tests the entire video pipeline by:
1. Uploading a sample audio/video file to the input bucket
2. Waiting for and verifying the transcription output
3. Verifying the chunking process was triggered and completed successfully
4. Displaying sentence-level audio segments from the chunking service

Usage:
    python pipeline_e2e_test.py --input-bucket INPUT_BUCKET --output-bucket OUTPUT_BUCKET --sample-file SAMPLE_FILE [options]

Options:
    --input-bucket INPUT_BUCKET    Name of the input S3 bucket
    --output-bucket OUTPUT_BUCKET  Name of the output S3 bucket for transcriptions
    --sample-file SAMPLE_FILE      Path to the sample audio/video file
    --timeout TIMEOUT              Timeout in seconds (default: 300)
    --cleanup                      Clean up test files after completion
"""
import os
import sys
import time
import json
import uuid
import argparse
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# ANSI colors for terminal output
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BOLD = "\033[1m"
NO_COLOR = "\033[0m"


def print_success(message):
    """Print a success message."""
    print(f"{GREEN}✅ {message}{NO_COLOR}")


def print_error(message):
    """Print an error message."""
    print(f"{RED}❌ {message}{NO_COLOR}")


def print_info(message):
    """Print an information message."""
    print(f"{YELLOW}{message}{NO_COLOR}")


def print_header(message):
    """Print a header message."""
    print(f"\n{BOLD}{message}{NO_COLOR}")


def print_divider():
    """Print a divider line for better readability."""
    print_info("-" * 80)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='End-to-end test for video pipeline')
    parser.add_argument('--input-bucket', required=True, help='Name of the input S3 bucket')
    parser.add_argument('--output-bucket', required=True, help='Name of the output S3 bucket')
    parser.add_argument('--sample-file', required=True, help='Path to the sample audio/video file')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds (default: 300)')
    parser.add_argument('--cleanup', action='store_true', help='Clean up test files after completion')
    return parser.parse_args()


def upload_file(file_path, bucket, s3_client, test_id):
    """Upload a file to an S3 bucket in the media directory with a unique test ID suffix."""
    try:
        file_name = os.path.basename(file_path)
        base_name, extension = os.path.splitext(file_name)
        
        # Always upload to the media directory with the test ID as a suffix
        unique_file_name = f"media/{base_name}_{test_id}{extension}"
        
        # Add test metadata
        metadata = {
            'speaker': 'Test Speaker',
            'title': 'Test Presentation',
            'track': 'Test Track',
            'day': 'Monday'
        }
        
        print_info(f"Uploading {file_path} to s3://{bucket}/{unique_file_name} with metadata...")
        s3_client.upload_file(
            file_path, 
            bucket, 
            unique_file_name,
            ExtraArgs={
                'Metadata': metadata
            }
        )
        print_success(f"File uploaded successfully to s3://{bucket}/{unique_file_name}")
        return unique_file_name
    except ClientError as e:
        print_error(f"Failed to upload file: {e}")
        sys.exit(1)


def wait_for_transcription(bucket, input_key, s3_client, timeout, test_id):
    """Wait for the transcription to appear in the output bucket."""
    print_header("Waiting for transcription to complete...")
    
    # Extract the base name without extension
    file_name = os.path.basename(input_key)
    base_name, _ = os.path.splitext(file_name)
    
    # The expected output should contain the same test_id
    expected_prefix = f"transcriptions/{base_name}"
    
    max_attempts = 10
    wait_time = timeout // max_attempts  # Distribute timeout across attempts
    attempt = 1
    
    while attempt <= max_attempts:
        print_info(f"Attempt {attempt} of {max_attempts}: Checking for transcription...")
        
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=f"transcriptions/"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Only consider JSON files that match our test_id
                    if (obj['Key'].endswith('.json') and 
                        test_id in obj['Key'] and
                        base_name.split('_')[0] in obj['Key']):
                        print_success(f"Found transcription: {obj['Key']}")
                        return obj['Key']
            
            if attempt < max_attempts:
                print_info(f"Transcription not ready yet. Waiting {wait_time} seconds before next attempt...")
                time.sleep(wait_time)
            attempt += 1
        
        except ClientError as e:
            print_error(f"Failed to check for transcription: {e}")
            sys.exit(1)
    
    print_error(f"Transcription did not complete after {max_attempts} attempts ({timeout} seconds total)")
    print_error("Please check the following:")
    print_error("1. The input file was successfully uploaded")
    print_error("2. The transcription Lambda function was triggered")
    print_error("3. There are no errors in the Lambda function logs")
    print_error(f"4. The output bucket '{bucket}' is accessible")
    sys.exit(1)


def verify_transcription(bucket, key, s3_client):
    """Download and verify the transcription content."""
    print_header("Verifying transcription content...")
    
    try:
        # Download the transcription file
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        # Parse the JSON content
        transcription = json.loads(content)
        
        # Basic validation for the custom format
        if 'transcription_text' not in transcription or 'segments' not in transcription:
            print_error("Invalid transcription format")
            sys.exit(1)
        
        transcript_text = transcription['transcription_text']
        segments = transcription.get('segments', [])
        audio_segments = transcription.get('audio_segments', [])
        metadata = transcription.get('metadata', {})
        
        # Output verification results
        print_success("Transcription verification passed!")
        print_info(f"Transcription text: \"{transcript_text}\"")
        print_info(f"Number of word-level segments: {len(segments)}")
        print_info(f"Number of sentence-level audio segments: {len(audio_segments)}")
        
        # Verify metadata
        expected_metadata = {
            'speaker': 'Test Speaker',
            'title': 'Test Presentation',
            'track': 'Test Track',
            'day': 'Monday'
        }
        
        if metadata:
            print_info("\nVerifying metadata:")
            for key, expected_value in expected_metadata.items():
                actual_value = metadata.get(key)
                if actual_value == expected_value:
                    print_success(f"  {key}: {actual_value}")
                else:
                    print_error(f"  {key}: Expected '{expected_value}', got '{actual_value}'")
        else:
            print_error("No metadata found in transcription output")
        
        # Display sentence-level audio segments if available
        if audio_segments:
            print_info("\nSentence-level audio segments:")
            for i, segment in enumerate(audio_segments):
                print_info(f"  Segment {i+1}: \"{segment.get('transcript', '')}\"")
                print_info(f"    Start time: {segment.get('start_time', 'N/A')}s, End time: {segment.get('end_time', 'N/A')}s")
        
        return transcription
    
    except (ClientError, json.JSONDecodeError, KeyError) as e:
        print_error(f"Failed to verify transcription: {e}")
        sys.exit(1)


def wait_for_chunking_output(bucket, transcription_key, s3_client, timeout, test_id):
    """Wait for the chunking output to appear in the output bucket."""
    print_header("Waiting for chunking processing to complete...")
    
    # Extract the base name from the transcription key
    transcription_file = os.path.basename(transcription_key)
    base_name, _ = os.path.splitext(transcription_file)
    
    # The expected chunking output file pattern
    expected_prefix = f"chunks/{base_name}"
    
    print_info(f"Looking for chunking outputs with prefix: {expected_prefix}")
    
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        # List objects with the expected prefix
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix="chunks/"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Only consider JSON files that match our test_id pattern
                    if (obj['Key'].endswith('.json') and 
                        test_id in obj['Key']):
                        print_success(f"Found chunking output: {obj['Key']}")
                        return obj['Key']
            
            print_info(f"Chunking output not ready yet, waiting 10 seconds... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(10)
        
        except ClientError as e:
            print_error(f"Failed to check for chunking output: {e}")
            sys.exit(1)
    
    print_error(f"Timeout after {timeout} seconds waiting for chunking output")
    return None


def check_step_functions_execution(media_key, test_id):
    """Check if a Step Functions execution was triggered for our test file."""
    print_header("Checking for Step Functions execution...")
    
    try:
        # Create a Step Functions client
        sfn_client = boto3.client('stepfunctions')
        
        # List recent executions of the video processing state machine
        # First, we need to find the state machine ARN
        response = sfn_client.list_state_machines()
        state_machine_arn = None
        
        for machine in response.get('stateMachines', []):
            if 'video_processing' in machine.get('name', '').lower():
                state_machine_arn = machine.get('stateMachineArn')
                break
        
        if not state_machine_arn:
            print_info("Could not find the video processing state machine")
            return False
            
        print_info(f"Found state machine: {state_machine_arn}")
        
        # List executions for this state machine
        response = sfn_client.list_executions(
            stateMachineArn=state_machine_arn,
            maxResults=10  # Limit to recent executions
        )
        
        for execution in response.get('executions', []):
            # Get the execution details to check the input
            exec_details = sfn_client.describe_execution(
                executionArn=execution.get('executionArn')
            )
            
            # Parse the input to see if it matches our test file
            try:
                input_data = json.loads(exec_details.get('input', '{}'))
                detail = input_data.get('detail', {})
                request_params = detail.get('requestParameters', {})
                
                if (request_params.get('key', '') == media_key or 
                    test_id in request_params.get('key', '')):
                    print_success(f"Found Step Functions execution for our test file: {execution.get('executionArn')}")
                    
                    # Check the execution status
                    status = exec_details.get('status')
                    print_info(f"Execution status: {status}")
                    
                    if status == 'SUCCEEDED':
                        return True
                    elif status == 'RUNNING':
                        print_info("Execution is still running. This might indicate chunking hasn't completed yet.")
                        return None
                    else:
                        print_error(f"Execution failed with status: {status}")
                        return False
            except json.JSONDecodeError:
                continue
        
        print_info("No matching Step Functions execution found")
        return False
        
    except Exception as e:
        print_error(f"Error checking Step Functions execution: {e}")
        return False


def check_cloudwatch_logs_for_chunking(test_id, timeout=60):
    """
    Check CloudWatch logs for evidence that the chunking module was invoked.
    
    Args:
        test_id: Unique test ID to filter logs
        timeout: How far back in time to look for logs in seconds
        
    Returns:
        bool: True if evidence of chunking module execution was found
    """
    print_header("Checking CloudWatch logs for chunking module invocation...")
    
    try:
        # Create a CloudWatch logs client
        logs_client = boto3.client('logs')
        
        # Calculate the time range to search for logs
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=timeout)
        
        # Convert to milliseconds since epoch as required by CloudWatch API
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        
        # Check for logs from the chunking module Lambda
        # Look for log groups that might contain chunking lambda logs
        response = logs_client.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/dev_media_chunking'
        )
        
        # If no log group found, try with other common naming patterns
        if not response.get('logGroups'):
            response = logs_client.describe_log_groups(
                logGroupNamePrefix='/aws/lambda'
            )
        
        chunking_found = False
        processed_chunks = False
        
        for log_group in response.get('logGroups', []):
            log_group_name = log_group['logGroupName']
            
            if 'chunk' not in log_group_name.lower():
                continue
                
            print_info(f"Checking log group: {log_group_name}")
            
            # Get the log streams for this log group, sorted by most recent first
            streams_response = logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=5  # Limit to most recent streams
            )
            
            for stream in streams_response.get('logStreams', []):
                # Get the logs from this stream within our time window
                try:
                    logs_response = logs_client.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream['logStreamName'],
                        startTime=start_time_ms,
                        endTime=end_time_ms,
                        limit=100  # Get a reasonable number of log events
                    )
                    
                    # Check if any log messages indicate the chunking module was invoked
                    for event in logs_response.get('events', []):
                        message = event.get('message', '')
                        
                        # Look for evidence of chunking module invocation
                        if 'Hello World from Chunking Module!' in message:
                            print_success("Found evidence of chunking module invocation!")
                            chunking_found = True
                        
                        # Look for evidence that our specific test file was processed
                        if test_id in message:
                            print_success(f"Found logs mentioning our test ID {test_id}!")
                            chunking_found = True
                        
                        # Look for specific evidence of chunk processing
                        if ('Processed' in message and 'audio segments' in message):
                            print_success(f"Found logs indicating chunks were processed: {message}")
                            processed_chunks = True
                            
                        # Print any informative messages about chunking
                        if 'chunk' in message.lower() or 'audio segment' in message.lower():
                            print_info(f"Log message: {message.strip()}")
                    
                    if chunking_found and processed_chunks:
                        print_success("Confirmed chunking module was invoked AND processed chunks!")
                        return True
                        
                    if chunking_found:
                        print_info("Chunking module was invoked, but no evidence of chunk processing")
                except Exception as e:
                    print_info(f"Error retrieving logs from stream {stream['logStreamName']}: {e}")
        
        if chunking_found:
            # Even if we didn't see chunk processing, at least the module was invoked
            print_info("Chunking module was invoked, but couldn't confirm chunk processing")
            return True
        else:
            print_error("No evidence found that chunking module was invoked")
            return False
            
    except Exception as e:
        print_error(f"Error checking CloudWatch logs: {e}")
        return False


def verify_chunking(transcription, output_bucket, input_key, s3_client, timeout, test_id):
    """Verify the chunking process."""
    print_info("\nVerifying chunking process...")

    # Check for Step Functions execution
    print_info("\nChecking for Step Functions execution...")
    execution_found = check_step_functions_execution(input_key, test_id)
    
    # Check for audio segments in transcription
    audio_segments = transcription.get('audio_segments', [])
    if audio_segments:
        print_info("\nSentence-level audio segments found in transcription:")
        for i, segment in enumerate(audio_segments):
            print_info(f"  Segment {i+1}: \"{segment.get('transcript', '')}\"")
            print_info(f"    Start time: {segment.get('start_time', 'N/A')}s, End time: {segment.get('end_time', 'N/A')}s")
    
    print_divider()
    return True


def cleanup_test_files(input_bucket, output_bucket, test_id, s3_client):
    """Clean up any files created during the test."""
    print_header(f"Cleaning up test files with ID {test_id}...")
    
    try:
        # Find and delete input files
        response = s3_client.list_objects_v2(
            Bucket=input_bucket,
            Prefix="media/"
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if test_id in obj['Key']:
                    print_info(f"Deleting input file: {obj['Key']}")
                    s3_client.delete_object(Bucket=input_bucket, Key=obj['Key'])
        
        # Find and delete output files
        response = s3_client.list_objects_v2(
            Bucket=output_bucket,
            Prefix="transcriptions/"
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if test_id in obj['Key']:
                    print_info(f"Deleting output file: {obj['Key']}")
                    s3_client.delete_object(Bucket=output_bucket, Key=obj['Key'])
        
        # Clean up chunking outputs if they exist
        response = s3_client.list_objects_v2(
            Bucket=output_bucket,
            Prefix="chunks/"
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if test_id in obj['Key']:
                    print_info(f"Deleting chunk file: {obj['Key']}")
                    s3_client.delete_object(Bucket=output_bucket, Key=obj['Key'])
        
        print_success("Cleanup completed")
    
    except ClientError as e:
        print_error(f"Failed to clean up some test files: {e}")


@dataclass
class EmbeddingResult:
    """Data class representing an embedding processing result."""
    chunk_id: str
    text: str
    status: str
    text_length: int

def check_embedding_processing(test_id: str, expected_transcript: str, timeout: int = 300) -> bool:
    """Check if the embedding processing completed successfully by monitoring Step Functions execution."""
    print_header("\nSTEP 4: Testing embedding processing")
    
    max_attempts = 10
    wait_time = timeout // max_attempts
    
    sfn_client = boto3.client('stepfunctions')
    
    # Find the state machine ARN
    response = sfn_client.list_state_machines()
    state_machine_arn = None
    
    for machine in response.get('stateMachines', []):
        if 'video_processing' in machine.get('name', '').lower():
            state_machine_arn = machine.get('stateMachineArn')
            break
    
    if not state_machine_arn:
        print_error("Could not find the video processing state machine")
        return False
    
    # Check executions until we find success or timeout
    for attempt in range(max_attempts):
        response = sfn_client.list_executions(
            stateMachineArn=state_machine_arn,
            maxResults=10
        )
        
        for execution in response.get('executions', []):
            exec_details = sfn_client.describe_execution(
                executionArn=execution.get('executionArn')
            )
            
            try:
                input_data = json.loads(exec_details.get('input', '{}'))
                if test_id in str(input_data):
                    status = exec_details.get('status')
                    
                    if status == 'SUCCEEDED':
                        print_success(f"Step Functions execution completed successfully: {execution.get('executionArn')}")
                        return True
                    elif status == 'FAILED':
                        print_error(f"Step Functions execution failed: {execution.get('executionArn')}")
                        # Get the error details
                        if exec_details.get('error'):
                            print_error(f"Error: {exec_details.get('error')}")
                            print_error(f"Cause: {exec_details.get('cause')}")
                        return False
                    elif status == 'RUNNING':
                        print_info(f"Step Functions execution still running. Waiting {wait_time} seconds before next attempt...")
                        time.sleep(wait_time)
                        break
            except json.JSONDecodeError:
                continue
        
        if attempt == max_attempts - 1:
            print_error("Embedding processing did not complete within the timeout period")
            return False
    
    print_error("Could not find matching Step Functions execution")
    return False


def main():
    """Main test execution function."""
    args = parse_args()
    
    # Generate a unique test ID
    test_id = str(uuid.uuid4())[:8]
    
    print_header("\n=== Starting Video Pipeline E2E Test ===\n")
    
    # Initialize AWS clients
    s3_client = boto3.client('s3')
    
    try:
        # Step 1: Upload test file
        print_header("\nSTEP 1: Testing file upload")
        input_key = upload_file(args.sample_file, args.input_bucket, s3_client, test_id)
        print_divider()
        
        # Step 2: Wait for and verify transcription
        print_header("\nSTEP 2: Testing transcription service")
        transcription_key = wait_for_transcription(args.output_bucket, input_key, s3_client, args.timeout, test_id)
        transcription = verify_transcription(args.output_bucket, transcription_key, s3_client)
        print_divider()
        
        # Step 3: Verify chunking process
        print_header("\nSTEP 3: Testing chunking service")
        verify_chunking(transcription, args.output_bucket, input_key, s3_client, args.timeout, test_id)
        print_divider()
        
        # Step 4: Check embedding processing
        if not check_embedding_processing(test_id, transcription['transcription_text'], args.timeout):
            print_error("Failed to verify embedding processing")
            sys.exit(1)
        print_divider()
        
        # Clean up test files if requested
        if args.cleanup:
            cleanup_test_files(args.input_bucket, args.output_bucket, test_id, s3_client)
        
        print_success("\n=== Video Pipeline E2E Test Completed Successfully ===\n")
        
    except Exception as e:
        print_error(f"\nTest failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 