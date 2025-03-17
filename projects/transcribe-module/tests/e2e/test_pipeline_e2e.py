#!/usr/bin/env python3
import os
import sys
import time
import json
import uuid
import argparse
import boto3
from botocore.exceptions import ClientError


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='End-to-end test for video transcription pipeline')
    parser.add_argument('--input-bucket', required=True, help='Name of the input S3 bucket')
    parser.add_argument('--output-bucket', required=True, help='Name of the output S3 bucket')
    parser.add_argument('--sample-file', required=True, help='Path to the sample audio/video file')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds (default: 300)')
    return parser.parse_args()


def upload_file(file_path, bucket, s3_client, test_id):
    """Upload a file to an S3 bucket in the media directory with a unique test ID suffix."""
    try:
        file_name = os.path.basename(file_path)
        base_name, extension = os.path.splitext(file_name)
        
        # Always upload to the media directory with the test ID as a suffix
        unique_file_name = f"media/{base_name}_{test_id}{extension}"
        
        print(f"Uploading {file_path} to s3://{bucket}/{unique_file_name}...")
        s3_client.upload_file(file_path, bucket, unique_file_name)
        print(f"✅ Upload successful")
        return unique_file_name
    except ClientError as e:
        print(f"❌ ERROR: Failed to upload file: {e}", file=sys.stderr)
        sys.exit(1)


def wait_for_transcription(bucket, input_key, s3_client, timeout):
    """Wait for the transcription to appear in the output bucket."""
    print("\nWaiting for transcription to complete...")
    
    # Extract the base name without test ID suffix or extension
    file_name = os.path.basename(input_key)
    # Get the base name (before the underscore where the test ID begins)
    base_name = file_name.split('_')[0]
    expected_prefix = f"transcriptions/{base_name}"
    
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        # List objects with the expected prefix
        try:
            response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=expected_prefix
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['Key'].endswith('.json'):
                        print(f"✅ Found transcription: {obj['Key']}")
                        return obj['Key']
            
            print(f"Transcription not ready yet, waiting 10 seconds... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(10)
        
        except ClientError as e:
            print(f"❌ ERROR: Failed to check for transcription: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"❌ ERROR: Timeout after {timeout} seconds waiting for transcription", file=sys.stderr)
    sys.exit(1)


def verify_transcription(bucket, key, s3_client):
    """Download and verify the transcription content."""
    print("\nVerifying transcription content...")
    
    try:
        # Download the transcription file
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        # Parse the JSON content
        transcription = json.loads(content)
        
        # Basic validation for the custom format
        if 'transcription_text' not in transcription or 'segments' not in transcription:
            print("❌ ERROR: Invalid transcription format", file=sys.stderr)
            sys.exit(1)
        
        transcript_text = transcription['transcription_text']
        segments = transcription.get('segments', [])
        
        # Output verification results
        print(f"✅ Verification passed!")
        print(f"Transcription text: \"{transcript_text}\"")
        print(f"Number of segments: {len(segments)}")
        
        return True
    
    except (ClientError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ ERROR: Failed to verify transcription: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to run the end-to-end test."""
    args = parse_args()
    
    # Print test header
    print("\n=== Starting Video Pipeline E2E Test ===\n")
    
    # Validate input file
    if not os.path.isfile(args.sample_file):
        print(f"❌ ERROR: Sample file not found: {args.sample_file}", file=sys.stderr)
        sys.exit(1)
    
    # Generate a unique test ID
    test_id = str(uuid.uuid4())[:8]
    
    # Create S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Upload the sample file to the input bucket in the media directory
        input_key = upload_file(args.sample_file, args.input_bucket, s3_client, test_id)
        
        # Wait for the transcription to appear in the output bucket
        output_key = wait_for_transcription(args.output_bucket, input_key, s3_client, args.timeout)
        
        # Verify the transcription content
        verify_transcription(args.output_bucket, output_key, s3_client)
        
        # Test passed
        print("\n✅ E2E TEST PASSED: Video pipeline is working correctly!")
        return 0
    
    except Exception as e:
        print(f"\n❌ E2E TEST FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 