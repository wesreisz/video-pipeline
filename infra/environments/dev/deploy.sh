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
VENV_DIR="$TRANSCRIBE_MODULE_DIR/.venv"

# Display header
echo -e "${BOLD}===== Video Pipeline Dev Deployment Script =====${NO_COLOR}"
echo -e "${YELLOW}Project root: ${PROJECT_ROOT}${NO_COLOR}"

# Function to activate virtual environment
activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "\n${YELLOW}Creating virtual environment...${NO_COLOR}"
        cd "$TRANSCRIBE_MODULE_DIR"
        python -m venv .venv
    fi
    
    echo -e "\n${YELLOW}Activating virtual environment...${NO_COLOR}"
    source "$VENV_DIR/bin/activate"
    
    echo -e "\n${YELLOW}Installing dependencies...${NO_COLOR}"
    pip install -q -r "$TRANSCRIBE_MODULE_DIR/requirements.txt"
    pip install -q -r "$TRANSCRIBE_MODULE_DIR/dev-requirements.txt"
}

# Function to run tests
run_tests() {
    echo -e "\n${BOLD}===== Running tests =====${NO_COLOR}"
    cd "$TRANSCRIBE_MODULE_DIR"
    
    # Run tests with pytest
    echo -e "\n${YELLOW}Running unit and integration tests...${NO_COLOR}"
    python -m pytest -xvs tests/ || {
        echo -e "\n${RED}Tests failed. Aborting deployment.${NO_COLOR}"
        exit 1
    }
    
    echo -e "\n${GREEN}All tests passed!${NO_COLOR}"
}

# Function to build the Lambda package
build_lambda_package() {
    echo -e "\n${BOLD}===== Building Lambda package =====${NO_COLOR}"
    
    # Create build directory if it doesn't exist
    mkdir -p "$BUILD_DIR"
    
    # Create a zip package for the Lambda function
    echo -e "\n${YELLOW}Creating zip package...${NO_COLOR}"
    cd "$PROJECT_ROOT"
    zip -r "$BUILD_DIR/transcribe_lambda.zip" "modules/transcribe-module/src/"
    
    echo -e "\n${GREEN}Lambda package built successfully: ${BUILD_DIR}/transcribe_lambda.zip${NO_COLOR}"
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

# Function to run end-to-end test
run_e2e_test() {
    echo -e "\n${BOLD}===== Running end-to-end test =====${NO_COLOR}"
    cd "$TRANSCRIBE_MODULE_DIR/tests/e2e"
    
    # Make the script executable if it's not already
    chmod +x run_e2e_test.sh
    
    # Run the end-to-end test with cleanup
    echo -e "\n${YELLOW}Executing end-to-end test...${NO_COLOR}"
    ./run_e2e_test.sh --cleanup || {
        echo -e "\n${RED}End-to-end test failed.${NO_COLOR}"
        exit 1
    }
    
    echo -e "\n${GREEN}End-to-end test successful!${NO_COLOR}"
}

# Main deployment flow
main() {
    # Step 1: Set up environment
    activate_venv
    
    # Step 2: Run tests
    run_tests
    
    # Step 3: Build Lambda package
    build_lambda_package
    
    # Step 4: Deploy with Terraform
    deploy_with_terraform
    
    # Step 5: Run end-to-end test to validate deployment
    run_e2e_test
    
    echo -e "\n${GREEN}${BOLD}===== Deployment completed successfully! =====${NO_COLOR}"
}

# Execute the main function
main 