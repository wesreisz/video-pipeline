#!/bin/bash
set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
NO_COLOR="\033[0m"

# Default values
SAMPLE_FILE_DEFAULT="$(pwd)/../../../../samples/hello-my_name_is_wes.mp3"
TIMEOUT_DEFAULT=300
TERRAFORM_DIR="$(pwd)/../../../../infra/environments/dev"
PROJECT_ROOT="$(pwd)/../../../../"
MODULE_ROOT="$(pwd)/../../"
REQUIREMENTS_FILE="${MODULE_ROOT}/dev-requirements.txt"
VENV_DIR="$(pwd)/.venv"
CLEANUP=false

# Usage information
function show_usage {
    echo -e "${BOLD}Usage:${NO_COLOR} $0 [options]"
    echo 
    echo "Options:"
    echo "  -f, --file PATH       Path to sample audio/video file (default: $SAMPLE_FILE_DEFAULT)"
    echo "  -t, --timeout SECONDS Timeout in seconds (default: $TIMEOUT_DEFAULT)"
    echo "  -v, --venv DIR        Virtual environment directory (default: $VENV_DIR)"
    echo "  --skip-venv           Skip virtual environment setup"
    echo "  -c, --cleanup         Clean up test files after completion"
    echo "  -h, --help            Show this help message"
    echo
    exit 1
}

# Parse command line arguments
SAMPLE_FILE=$SAMPLE_FILE_DEFAULT
TIMEOUT=$TIMEOUT_DEFAULT
SKIP_VENV=false
CLEANUP=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--file)
            SAMPLE_FILE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -v|--venv)
            VENV_DIR="$2"
            shift 2
            ;;
        --skip-venv)
            SKIP_VENV=true
            shift
            ;;
        -c|--cleanup)
            CLEANUP=true
            shift
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NO_COLOR}"
            show_usage
            ;;
    esac
done

# Check if the sample file exists
if [[ ! -f "$SAMPLE_FILE" ]]; then
    echo -e "${RED}ERROR: Sample file not found: $SAMPLE_FILE${NO_COLOR}"
    exit 1
fi

# Check if requirements.txt exists
if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    echo -e "${RED}ERROR: Requirements file not found: $REQUIREMENTS_FILE${NO_COLOR}"
    exit 1
fi

# Function to setup virtual environment
function setup_venv {
    if [ "$SKIP_VENV" = true ]; then
        echo -e "${YELLOW}Skipping virtual environment setup...${NO_COLOR}"
        return
    fi

    echo -e "\n${BOLD}=== Setting up Python Virtual Environment ===${NO_COLOR}\n"
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: Python 3 is not installed or not in PATH.${NO_COLOR}"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Creating virtual environment at $VENV_DIR...${NO_COLOR}"
        python3 -m venv "$VENV_DIR"
    else
        echo -e "${YELLOW}Using existing virtual environment at $VENV_DIR...${NO_COLOR}"
    fi
    
    # Activate virtual environment
    echo -e "${YELLOW}Activating virtual environment...${NO_COLOR}"
    source "$VENV_DIR/bin/activate"
    
    # Install requirements
    echo -e "${YELLOW}Installing requirements from $REQUIREMENTS_FILE...${NO_COLOR}"
    pip install -q -r "$REQUIREMENTS_FILE"
    
    echo -e "${GREEN}✅ Virtual environment setup complete!${NO_COLOR}"
}

# Function to extract Terraform outputs
function get_terraform_output {
    local output_name=$1
    
    echo -e "${YELLOW}Extracting $output_name from Terraform outputs...${NO_COLOR}"
    
    # Change to the Terraform directory
    pushd "$TERRAFORM_DIR" > /dev/null
    
    # Try to get the Terraform output
    if ! output_value=$(terraform output -raw "$output_name" 2>/dev/null); then
        echo -e "${RED}ERROR: Failed to get Terraform output '$output_name'.${NO_COLOR}"
        echo -e "${YELLOW}Make sure Terraform has been applied successfully.${NO_COLOR}"
        popd > /dev/null
        exit 1
    fi
    
    popd > /dev/null
    echo "$output_value"
}

# Setup virtual environment
setup_venv

# Get bucket names from Terraform outputs
echo -e "\n${BOLD}=== Preparing Video Pipeline E2E Test ===${NO_COLOR}\n"

# Change to the Terraform directory to get outputs
pushd "$TERRAFORM_DIR" > /dev/null
echo -e "${YELLOW}Extracting bucket information from Terraform...${NO_COLOR}"

# Try to get the input bucket name
if ! INPUT_BUCKET=$(terraform output -raw media_bucket_name 2>/dev/null); then
    echo -e "${RED}ERROR: Failed to get media_bucket_name from Terraform.${NO_COLOR}"
    echo -e "${YELLOW}Make sure Terraform has been applied successfully.${NO_COLOR}"
    popd > /dev/null
    exit 1
fi

# Try to get the output bucket name
if ! OUTPUT_BUCKET=$(terraform output -raw transcription_bucket_name 2>/dev/null); then
    echo -e "${RED}ERROR: Failed to get transcription_bucket_name from Terraform.${NO_COLOR}"
    echo -e "${YELLOW}Make sure Terraform has been applied successfully.${NO_COLOR}"
    popd > /dev/null
    exit 1
fi
popd > /dev/null

echo -e "${GREEN}Input bucket:${NO_COLOR} $INPUT_BUCKET"
echo -e "${GREEN}Output bucket:${NO_COLOR} $OUTPUT_BUCKET"
echo -e "${GREEN}Sample file:${NO_COLOR} $SAMPLE_FILE"
echo -e "${GREEN}Timeout:${NO_COLOR} $TIMEOUT seconds"
if [ "$CLEANUP" = true ]; then
    echo -e "${GREEN}Cleanup:${NO_COLOR} Enabled"
fi

# Check for AWS credentials
if [[ -z "$AWS_ACCESS_KEY_ID" ]] || [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    if [[ ! -f "$HOME/.aws/credentials" ]] && [[ ! -f "$HOME/.aws/config" ]]; then
        echo -e "\n${RED}WARNING: AWS credentials not found.${NO_COLOR}"
        echo -e "${YELLOW}Make sure you have AWS credentials configured via environment variables or AWS CLI.${NO_COLOR}"
    fi
fi

# Run the Python E2E test script
echo -e "\n${BOLD}=== Running E2E Test ===${NO_COLOR}\n"

# Make the Python script executable if it's not already
SCRIPT_PATH="$(dirname "$0")/test_pipeline_e2e.py"
chmod +x "$SCRIPT_PATH"

# Build command with conditional cleanup flag
COMMAND_ARGS=(
    "--input-bucket" "$INPUT_BUCKET"
    "--output-bucket" "$OUTPUT_BUCKET"
    "--sample-file" "$SAMPLE_FILE"
    "--timeout" "$TIMEOUT"
)

if [ "$CLEANUP" = true ]; then
    COMMAND_ARGS+=("--cleanup")
fi

# Run the test script (ensure we use the python from the virtual environment if enabled)
if [ "$SKIP_VENV" = false ]; then
    "$VENV_DIR/bin/python" "$SCRIPT_PATH" "${COMMAND_ARGS[@]}"
else
    "$SCRIPT_PATH" "${COMMAND_ARGS[@]}"
fi

# Check the exit code
EXIT_CODE=$?
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "\n${BOLD}${GREEN}E2E Test completed successfully!${NO_COLOR}"
else
    echo -e "\n${BOLD}${RED}E2E Test failed with exit code $EXIT_CODE${NO_COLOR}"
fi

# Deactivate virtual environment if we enabled it
if [ "$SKIP_VENV" = false ]; then
    if type deactivate > /dev/null 2>&1; then
        deactivate
    fi
fi

exit $EXIT_CODE 