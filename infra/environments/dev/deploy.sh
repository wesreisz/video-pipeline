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
SHARED_LIBS_DIR="$MODULES_DIR/shared_libs"
TRANSCRIBE_VENV_DIR="$TRANSCRIBE_MODULE_DIR/.venv"
CHUNKING_VENV_DIR="$CHUNKING_MODULE_DIR/.venv"

# Display header
echo -e "${BOLD}===== Video Pipeline Dev Deployment Script =====${NO_COLOR}"
echo -e "${YELLOW}Project root: ${PROJECT_ROOT}${NO_COLOR}"

# Function to check if shared_libs requirements.txt exists, create if not
ensure_shared_libs_requirements() {
    if [ ! -f "$SHARED_LIBS_DIR/requirements.txt" ]; then
        echo -e "\n${YELLOW}Creating requirements.txt for shared_libs...${NO_COLOR}"
        echo "boto3>=1.26.0" > "$SHARED_LIBS_DIR/requirements.txt"
        echo "# Add other dependencies as needed" >> "$SHARED_LIBS_DIR/requirements.txt"
    fi
}

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
    
    # Also install shared_libs dependencies
    if [ -f "$SHARED_LIBS_DIR/requirements.txt" ]; then
        echo -e "\n${YELLOW}Installing shared_libs dependencies...${NO_COLOR}"
        pip install -q -r "$SHARED_LIBS_DIR/requirements.txt"
    fi
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
    
    # Also install shared_libs dependencies
    if [ -f "$SHARED_LIBS_DIR/requirements.txt" ]; then
        echo -e "\n${YELLOW}Installing shared_libs dependencies...${NO_COLOR}"
        pip install -q -r "$SHARED_LIBS_DIR/requirements.txt"
    fi
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
    
}

# Function to build the Lambda packages
build_lambda_packages() {
    echo -e "\n${BOLD}===== Building Lambda packages =====${NO_COLOR}"
    
    # Create build directory if it doesn't exist
    mkdir -p "$BUILD_DIR"
    
    # Create a zip package for the transcribe Lambda function
    echo -e "\n${YELLOW}Creating transcribe module zip package...${NO_COLOR}"
    cd "$PROJECT_ROOT"
    
    # Include shared_libs in the transcribe module package
    echo -e "\n${YELLOW}Including shared_libs in transcribe module package...${NO_COLOR}"
    zip -r "$BUILD_DIR/transcribe_lambda.zip" "modules/transcribe-module/src/" "modules/shared_libs/"
    
    echo -e "\n${GREEN}Transcribe Lambda package built successfully: ${BUILD_DIR}/transcribe_lambda.zip${NO_COLOR}"
    
    # Create a zip package for the chunking Lambda function
    echo -e "\n${YELLOW}Creating chunking module zip package...${NO_COLOR}"
    cd "$PROJECT_ROOT"
    
    # Include shared_libs in the chunking module package
    echo -e "\n${YELLOW}Including shared_libs in chunking module package...${NO_COLOR}"
    zip -r "$BUILD_DIR/chunking_lambda.zip" "modules/chunking-module/src/" "modules/shared_libs/"
    
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

# Function to run consolidated end-to-end test
run_consolidated_e2e_test() {
    echo -e "\n${BOLD}===== Running consolidated pipeline end-to-end test =====${NO_COLOR}"
    cd "$PROJECT_ROOT/tests/e2e"
    
    # Make the script executable if it's not already
    chmod +x run_e2e_test.sh
    
    # Run the end-to-end test with cleanup
    echo -e "\n${YELLOW}Executing consolidated pipeline end-to-end test...${NO_COLOR}"
    ./run_e2e_test.sh --cleanup || {
        echo -e "\n${RED}Consolidated pipeline end-to-end test failed.${NO_COLOR}"
        exit 1
    }
    
    echo -e "\n${GREEN}Consolidated pipeline end-to-end test successful!${NO_COLOR}"
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
    
    # Step 5: Run consolidated end-to-end test to validate deployment
    run_consolidated_e2e_test
    
    echo -e "\n${GREEN}${BOLD}===== Deployment completed successfully! =====${NO_COLOR}"
}

# Execute the main function
main 