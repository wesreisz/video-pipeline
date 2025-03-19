#!/bin/bash

# Chunking Module End-to-End Test
# This script tests the chunking module by uploading a sample transcription file to S3
# and verifying that it gets processed correctly.

set -e  # Exit on error

# Text formatting for output
BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NO_COLOR="\033[0m"

# Configuration
TRANSCRIPTION_BUCKET="dev-media-transcribe-output"
CHUNKING_BUCKET="dev-media-chunking-output"
TEST_FILE="test_transcription.json"
TEST_KEY="transcriptions/${TEST_FILE}"
EXPECTED_OUTPUT_KEY="chunks/${TEST_FILE%.json}-chunks.json"
MAX_WAIT_TIME=60  # Maximum time to wait in seconds
CLEANUP_FLAG="--cleanup"

# Check if cleanup flag is provided
CLEANUP=false
if [[ "$1" == "$CLEANUP_FLAG" ]]; then
    CLEANUP=true
fi

# Display header
echo -e "${BOLD}===== Chunking Module End-to-End Test =====${NO_COLOR}"

# Create a test transcription file
create_test_file() {
    echo -e "\n${YELLOW}Creating test transcription file...${NO_COLOR}"
    
    # Create a temporary directory if it doesn't exist
    mkdir -p tmp
    
    # Current timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create a sample transcription file
    cat > tmp/${TEST_FILE} << EOL
{
  "original_file": "sample.mp3",
  "transcription_text": "This is a sample transcription for testing the chunking module.",
  "timestamp": "${TIMESTAMP}",
  "job_name": "test-job-$(uuidgen || date +%s)",
  "media_type": "audio",
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 5.0,
      "text": "This is a sample transcription"
    },
    {
      "start_time": 5.0,
      "end_time": 10.0,
      "text": "for testing the chunking module."
    }
  ]
}
EOL
    
    echo -e "${GREEN}Test file created: tmp/${TEST_FILE}${NO_COLOR}"
}

# Upload the test file to S3
upload_test_file() {
    echo -e "\n${YELLOW}Uploading test file to S3...${NO_COLOR}"
    aws s3 cp tmp/${TEST_FILE} s3://${TRANSCRIPTION_BUCKET}/${TEST_KEY}
    echo -e "${GREEN}Test file uploaded to s3://${TRANSCRIPTION_BUCKET}/${TEST_KEY}${NO_COLOR}"
}

# Wait for the chunking process to complete
wait_for_output() {
    echo -e "\n${YELLOW}Waiting for chunking to complete...${NO_COLOR}"
    
    WAIT_TIME=0
    while [ $WAIT_TIME -lt $MAX_WAIT_TIME ]; do
        if aws s3 ls s3://${CHUNKING_BUCKET}/${EXPECTED_OUTPUT_KEY} >/dev/null 2>&1; then
            echo -e "${GREEN}Output file found: s3://${CHUNKING_BUCKET}/${EXPECTED_OUTPUT_KEY}${NO_COLOR}"
            return 0
        fi
        
        echo -n "."
        sleep 5
        WAIT_TIME=$((WAIT_TIME + 5))
    done
    
    echo -e "\n${RED}Timed out waiting for output file${NO_COLOR}"
    return 1
}

# Verify the chunking output
verify_output() {
    echo -e "\n${YELLOW}Verifying chunking output...${NO_COLOR}"
    
    # Download the output file
    mkdir -p tmp/output
    aws s3 cp s3://${CHUNKING_BUCKET}/${EXPECTED_OUTPUT_KEY} tmp/output/ || {
        echo -e "${RED}Failed to download output file${NO_COLOR}"
        return 1
    }
    
    # Check if the output file contains the expected content
    OUTPUT_FILE="tmp/output/$(basename ${EXPECTED_OUTPUT_KEY})"
    
    # Check if the file exists and is valid JSON
    if [ ! -f "$OUTPUT_FILE" ]; then
        echo -e "${RED}Output file does not exist: ${OUTPUT_FILE}${NO_COLOR}"
        return 1
    fi
    
    # Try to parse the JSON
    cat "$OUTPUT_FILE" | jq . >/dev/null 2>&1 || {
        echo -e "${RED}Output file is not valid JSON${NO_COLOR}"
        return 1
    }
    
    echo -e "${GREEN}Chunking output verified successfully${NO_COLOR}"
    return 0
}

# Clean up test files
cleanup() {
    if [ "$CLEANUP" = true ]; then
        echo -e "\n${YELLOW}Cleaning up test files...${NO_COLOR}"
        
        # Remove the test file from S3
        aws s3 rm s3://${TRANSCRIPTION_BUCKET}/${TEST_KEY}
        
        # Remove the output file from S3
        aws s3 rm s3://${CHUNKING_BUCKET}/${EXPECTED_OUTPUT_KEY}
        
        # Remove local files
        rm -rf tmp
        
        echo -e "${GREEN}Cleanup completed${NO_COLOR}"
    else
        echo -e "\n${YELLOW}Skipping cleanup. Test files remain in S3 and local tmp directory.${NO_COLOR}"
        echo -e "${YELLOW}To clean up, run this script with the ${CLEANUP_FLAG} flag.${NO_COLOR}"
    fi
}

# Main test flow
main() {
    # Step 1: Create test file
    create_test_file
    
    # Step 2: Upload test file to S3
    upload_test_file
    
    # Step 3: Wait for the chunking process to complete
    wait_for_output
    
    # Step 4: Verify the chunking output
    verify_output
    
    # Step 5: Clean up
    cleanup
    
    echo -e "\n${GREEN}${BOLD}===== End-to-End Test Completed Successfully! =====${NO_COLOR}"
}

# Run the test
main || {
    echo -e "\n${RED}${BOLD}===== End-to-End Test Failed! =====${NO_COLOR}"
    exit 1
}

exit 0 