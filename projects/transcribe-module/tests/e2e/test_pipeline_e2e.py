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
    parser.add_argument('--cleanup', action='store_true', help='Clean up test files after completion')
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


def wait_for_transcription(bucket, input_key, s3_client, timeout, test_id):
    """Wait for the transcription to appear in the output bucket."""
    print("\nWaiting for transcription to complete...")
    
    # Extract the base name without extension
    file_name = os.path.basename(input_key)
    base_name, _ = os.path.splitext(file_name)
    
    # The expected output should contain the same test_id
    # Format is likely: transcriptions/hello-my_name_is_wes_<test_id>.json
    expected_prefix = f"transcriptions/{base_name}"
    
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        # List objects with the expected prefix
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


def cleanup_test_files(input_bucket, output_bucket, test_id, s3_client):
    """Clean up any files created during the test."""
    print(f"\nCleaning up test files with ID {test_id}...")
    
    try:
        # Find and delete input files
        response = s3_client.list_objects_v2(
            Bucket=input_bucket,
            Prefix="media/"
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if test_id in obj['Key']:
                    print(f"Deleting input file: {obj['Key']}")
                    s3_client.delete_object(Bucket=input_bucket, Key=obj['Key'])
        
        # Find and delete output files
        response = s3_client.list_objects_v2(
            Bucket=output_bucket,
            Prefix="transcriptions/"
        )
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if test_id in obj['Key']:
                    print(f"Deleting output file: {obj['Key']}")
                    s3_client.delete_object(Bucket=output_bucket, Key=obj['Key'])
        
        print("✅ Cleanup completed")
    
    except ClientError as e:
        print(f"⚠️ WARNING: Failed to clean up some test files: {e}", file=sys.stderr)


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
    
    # Clean up any existing test files before starting
    if args.cleanup:
        # Find and delete existing files from previous tests
        print("\nCleaning up existing test files...")
        try:
            # Check input bucket
            response = s3_client.list_objects_v2(
                Bucket=args.input_bucket,
                Prefix="media/"
            )
            if 'Contents' in response:
                for obj in response['Contents']:
                    if "_" in obj['Key'] and obj['Key'].startswith("media/"):
                        file_name = os.path.basename(args.sample_file)
                        base_name, _ = os.path.splitext(file_name)
                        if base_name.split('_')[0] in obj['Key']:
                            print(f"Deleting old input file: {obj['Key']}")
                            s3_client.delete_object(Bucket=args.input_bucket, Key=obj['Key'])
            
            # Check output bucket
            response = s3_client.list_objects_v2(
                Bucket=args.output_bucket,
                Prefix="transcriptions/"
            )
            if 'Contents' in response:
                for obj in response['Contents']:
                    if "_" in obj['Key'] and obj['Key'].endswith(".json"):
                        file_name = os.path.basename(args.sample_file)
                        base_name, _ = os.path.splitext(file_name)
                        if base_name.split('_')[0] in obj['Key']:
                            print(f"Deleting old output file: {obj['Key']}")
                            s3_client.delete_object(Bucket=args.output_bucket, Key=obj['Key'])
        except ClientError as e:
            print(f"⚠️ WARNING: Error during cleanup of existing files: {e}")
    
    try:
        # Upload the sample file to the input bucket in the media directory
        input_key = upload_file(args.sample_file, args.input_bucket, s3_client, test_id)
        
        # Wait for the transcription to appear in the output bucket
        output_key = wait_for_transcription(args.output_bucket, input_key, s3_client, args.timeout, test_id)
        
        # Verify the transcription content
        verify_transcription(args.output_bucket, output_key, s3_client)
        
        # Test passed
        print("\n✅ E2E TEST PASSED: Video pipeline is working correctly!")
        
        # Clean up test files if requested
        if args.cleanup:
            cleanup_test_files(args.input_bucket, args.output_bucket, test_id, s3_client)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ E2E TEST FAILED: {e}", file=sys.stderr)
        return 1
    finally:
        # Always attempt to clean up if cleanup is enabled, even if test fails
        if args.cleanup and 'test_id' in locals():
            cleanup_test_files(args.input_bucket, args.output_bucket, test_id, s3_client)


if __name__ == "__main__":
    sys.exit(main()) 