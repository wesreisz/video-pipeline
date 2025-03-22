#!/bin/bash

# Video Pipeline Dev Deployment Script
# This script builds and deploys the video pipeline project to the development environment.

set -e  # Exit on error

# Text formatting for output
BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NO_COLOR="\033[0m"

# Define paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infra"
BUILD_DIR="$INFRA_DIR/build"
MODULES_DIR="$PROJECT_ROOT/modules"
TRANSCRIBE_MODULE_DIR="$MODULES_DIR/transcribe-module"
CHUNKING_MODULE_DIR="$MODULES_DIR/chunking-module"
TRANSCRIBE_VENV_DIR="$TRANSCRIBE_MODULE_DIR/.venv"
CHUNKING_VENV_DIR="$CHUNKING_MODULE_DIR/.venv"

# Display header
echo -e "${BOLD}===== Video Pipeline Dev Deployment Script =====${NO_COLOR}"
echo -e "${YELLOW}Project root: ${PROJECT_ROOT}${NO_COLOR}"

# Function to activate virtual environment for transcribe module
activate_transcribe_venv() {
    if [ ! -d "$TRANSCRIBE_VENV_DIR" ]; then
        echo -e "\n${YELLOW}Creating virtual environment for transcribe module...${NO_COLOR}"
        cd "$TRANSCRIBE_MODULE_DIR"
        python -m venv .venv
    fi
    
    echo -e "\n${YELLOW}Activating virtual environment for transcribe module...${NO_COLOR}"
    source "$TRANSCRIBE_VENV_DIR/bin/activate"
    
    echo -e "\n${YELLOW}Installing dependencies for transcribe module...${NO_COLOR}"
    pip install -q -r "$TRANSCRIBE_MODULE_DIR/requirements.txt"
    pip install -q -r "$TRANSCRIBE_MODULE_DIR/dev-requirements.txt"
}

# Function to activate virtual environment for chunking module
activate_chunking_venv() {
    if [ ! -d "$CHUNKING_VENV_DIR" ]; then
        echo -e "\n${YELLOW}Creating virtual environment for chunking module...${NO_COLOR}"
        cd "$CHUNKING_MODULE_DIR"
        python -m venv .venv
    fi
    
    echo -e "\n${YELLOW}Activating virtual environment for chunking module...${NO_COLOR}"
    source "$CHUNKING_VENV_DIR/bin/activate"
    
    echo -e "\n${YELLOW}Installing dependencies for chunking module...${NO_COLOR}"
    pip install -q -r "$CHUNKING_MODULE_DIR/requirements.txt"
    pip install -q -r "$CHUNKING_MODULE_DIR/dev-requirements.txt"
}

# Function to run tests for transcribe module
run_transcribe_tests() {
    echo -e "\n${BOLD}===== Running transcribe module tests =====${NO_COLOR}"
    cd "$TRANSCRIBE_MODULE_DIR"
    
    # Run tests with pytest, excluding integration tests
    echo -e "\n${YELLOW}Running unit tests for transcribe module...${NO_COLOR}"
    python -m pytest -xvs tests/ --ignore=tests/integration || {
        echo -e "\n${RED}Transcribe module tests failed. Aborting deployment.${NO_COLOR}"
        exit 1
    }
    
    echo -e "\n${GREEN}All transcribe module tests passed!${NO_COLOR}"
}

# Function to run tests for chunking module
run_chunking_tests() {
    echo -e "\n${BOLD}===== Running chunking module tests =====${NO_COLOR}"
    cd "$CHUNKING_MODULE_DIR"
    
    # Run tests with pytest and coverage
    echo -e "\n${YELLOW}Running tests for chunking module...${NO_COLOR}"
    coverage_output=$(python -m pytest tests/ -v --cov=src.handlers --cov-report=term-missing)
    exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo -e "\n${RED}Chunking module tests failed. Aborting deployment.${NO_COLOR}"
        exit 1
    fi
    
    # Extract coverage percentage
    coverage_percentage=$(echo "$coverage_output" | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
    
    if (( $(echo "$coverage_percentage < 90" | bc -l) )); then
        echo -e "\n${RED}Test coverage is below 90%. Current coverage: ${coverage_percentage}%. Aborting deployment.${NO_COLOR}"
        exit 1
    fi
    
    echo -e "\n${GREEN}All chunking module tests passed with sufficient coverage!${NO_COLOR}"
}

# Function to build the Lambda packages
build_lambda_packages() {
    echo -e "\n${BOLD}===== Building Lambda packages =====${NO_COLOR}"
    
    # Create build directory if it doesn't exist
    mkdir -p "$BUILD_DIR"
    
    # Create a zip package for the transcribe Lambda function
    echo -e "\n${YELLOW}Creating transcribe module zip package...${NO_COLOR}"
    cd "$PROJECT_ROOT"
    zip -r "$BUILD_DIR/transcribe_lambda.zip" "modules/transcribe-module/src/"
    
    echo -e "\n${GREEN}Transcribe Lambda package built successfully: ${BUILD_DIR}/transcribe_lambda.zip${NO_COLOR}"
    
    # Create a zip package for the chunking Lambda function
    echo -e "\n${YELLOW}Creating chunking module zip package...${NO_COLOR}"
    cd "$PROJECT_ROOT"
    zip -r "$BUILD_DIR/chunking_lambda.zip" "modules/chunking-module/src/"
    
    echo -e "\n${GREEN}Chunking Lambda package built successfully: ${BUILD_DIR}/chunking_lambda.zip${NO_COLOR}"
}

# Function to deploy using Terraform
deploy_with_terraform() {
    echo -e "\n${BOLD}===== Deploying with Terraform =====${NO_COLOR}"
    cd "$SCRIPT_DIR"
    
    echo -e "\n${YELLOW}Initializing Terraform...${NO_COLOR}"
    terraform init
    
    echo -e "\n${YELLOW}Creating Terraform plan...${NO_COLOR}"
    terraform plan -out=tfplan
    
    echo -e "\n${YELLOW}Applying Terraform plan...${NO_COLOR}"
    terraform apply "tfplan"
    
    echo -e "\n${GREEN}Deployment successful!${NO_COLOR}"
}

# Function to check AWS resources
check_aws_resources() {
    echo -e "\n${BOLD}===== Checking AWS Resources Status=====${NO_COLOR}"
    
    # Check S3 buckets
    echo -e "\n${YELLOW}Checking S3 buckets...${NO_COLOR}"
    aws s3api head-bucket --bucket "dev-media-transcribe-input" 2>/dev/null || {
        echo -e "\n${RED}Input bucket 'dev-media-transcribe-input' is not accessible.${NO_COLOR}"
        exit 1
    }
    aws s3api head-bucket --bucket "dev-media-transcribe-output" 2>/dev/null || {
        echo -e "\n${RED}Output bucket 'dev-media-transcribe-output' is not accessible.${NO_COLOR}"
        exit 1
    }
    echo -e "${GREEN}S3 buckets are accessible.${NO_COLOR}"
    
    # Check Step Functions state machine
    echo -e "\n${YELLOW}Checking Step Functions state machine...${NO_COLOR}"
    aws stepfunctions describe-state-machine --state-machine-arn "$(terraform output -raw sfn_state_machine_arn)" || {
        echo -e "\n${RED}Step Functions state machine 'dev_video_processing' is not accessible.${NO_COLOR}"
        exit 1
    }
    echo -e "${GREEN}Step Functions state machine is accessible.${NO_COLOR}"
}

# Function to check AWS resource readiness with retries
check_aws_resource_readiness() {
    echo -e "\n${BOLD}===== Checking AWS Resource Readiness =====${NO_COLOR}"
    local max_attempts=12
    local wait_time=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "\n${YELLOW}Attempt $attempt of $max_attempts: Checking resource readiness...${NO_COLOR}"
        
        # Check Lambda function status
        echo -e "${YELLOW}Checking Lambda functions...${NO_COLOR}"
        local lambda_ready=true
        
        # Get Lambda function names from Terraform output
        local transcribe_function=$(terraform output -raw transcribe_lambda_function_name)
        local chunking_function=$(terraform output -raw chunking_lambda_function_name)
        
        # Check each Lambda function
        for func in "$transcribe_function" "$chunking_function"; do
            echo -e "Checking Lambda function: $func"
            if ! aws lambda get-function --function-name "$func" --query 'Configuration.State' | grep -q "Active"; then
                lambda_ready=false
                break
            fi
        done
        
        # Check Step Functions state machine
        echo -e "${YELLOW}Checking Step Functions state machine...${NO_COLOR}"
        local sfn_arn=$(terraform output -raw sfn_state_machine_arn)
        local sfn_ready=false
        
        if aws stepfunctions describe-state-machine --state-machine-arn "$sfn_arn" --query 'status' | grep -q "ACTIVE"; then
            sfn_ready=true
        fi
        
        # If all checks pass, we're ready
        if [ "$lambda_ready" = true ] && [ "$sfn_ready" = true ]; then
            echo -e "\n${GREEN}All AWS resources are ready!${NO_COLOR}"
            return 0
        fi
        
        echo -e "\n${YELLOW}Resources not ready yet. Waiting $wait_time seconds before next attempt...${NO_COLOR}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    echo -e "\n${RED}Timeout waiting for AWS resources to be ready. Please check the AWS Console for more details.${NO_COLOR}"
    return 1
}

# Function to run consolidated end-to-end test
run_e2e_test() {
    echo -e "\n${BOLD}===== Running end-to-end tests =====${NO_COLOR}"
    cd "$PROJECT_ROOT/tests/e2e"
    
    # Make the script executable if it's not already
    chmod +x run_e2e_test.sh
    
    # Run the end-to-end test with cleanup
    echo -e "\n${YELLOW}Executing pipeline end-to-end test...${NO_COLOR}"
    ./run_e2e_test.sh --cleanup || {
        echo -e "\n${RED}Consolidated pipeline end-to-end test failed.${NO_COLOR}"
        exit 1
    }

    # Add SQS verification
    echo -e "\n${YELLOW}Verifying SQS message delivery...${NO_COLOR}"
    
    # Wait for messages to appear in the queue (up to 30 seconds)
    local max_attempts=6
    local attempt=1
    local messages_found=false
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "Checking SQS queue (attempt $attempt of $max_attempts)..."
        
        # Get messages from the queue
        local queue_messages=$(aws sqs receive-message \
            --queue-url https://sqs.us-east-1.amazonaws.com/855007292085/audio_segments_queue \
            --max-number-of-messages 10 2>/dev/null)
        
        # Check if messages exist
        if echo "$queue_messages" | grep -q "MessageId"; then
            echo -e "\n${GREEN}✓ Messages found in SQS queue${NO_COLOR}"
            echo -e "Queue contents:"
            echo "$queue_messages" | jq -r '.Messages[] | "MessageId: \(.MessageId)\nBody: \(.Body)\n"'
            messages_found=true
            break
        fi
        
        echo "No messages found yet, waiting 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    if [ "$messages_found" = false ]; then
        echo -e "\n${RED}No messages found in SQS queue after ${max_attempts} attempts.${NO_COLOR}"
        exit 1
    fi
    
    echo -e "\n${GREEN}Consolidated E2E Test completed successfully!${NO_COLOR}"
}

# Main deployment flow
main() {
    # Step 1: Set up environments
    activate_transcribe_venv
    activate_chunking_venv
    
    # Step 2: Run tests
    run_transcribe_tests
    run_chunking_tests
    
    # Step 3: Build Lambda packages
    build_lambda_packages
    
    # Step 4: Deploy with Terraform
    deploy_with_terraform
    
    # Step 5: Check AWS resources
    check_aws_resources
    
    # Step 6: Wait for resources to be fully ready
    check_aws_resource_readiness || {
        echo -e "\n${RED}AWS resources did not become ready in time. Aborting end-to-end tests.${NO_COLOR}"
        exit 1
    }
    
    # Step 7: Run consolidated end-to-end test to validate deployment
    run_e2e_test
    
    echo -e "\n${GREEN}${BOLD}===== Deployment completed successfully! =====${NO_COLOR}"
}

# Execute the main function
main 