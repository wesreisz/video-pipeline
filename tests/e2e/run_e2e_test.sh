#!/bin/bash
# Consolidated End-to-End Test Runner for Video Pipeline

# ANSI colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BOLD="\033[1m"
NO_COLOR="\033[0m"

# Default configuration
INPUT_BUCKET="dev-media-transcribe-input"
OUTPUT_BUCKET="dev-media-transcribe-output"
SAMPLE_FILE="./samples/hello-my_name_is_wes.mp3"
TIMEOUT=300
CLEANUP=false
VENV_PATH=""


# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Function to display usage information
function display_usage {
    echo -e "${BOLD}Usage:${NO_COLOR} $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --input-bucket BUCKET   Specify the input S3 bucket (default: $INPUT_BUCKET)"
    echo "  --output-bucket BUCKET  Specify the output S3 bucket (default: $OUTPUT_BUCKET)"
    echo "  --file FILE             Path to the sample audio/video file (default: $SAMPLE_FILE)"
    echo "  --timeout SECONDS       Maximum waiting time in seconds (default: $TIMEOUT)"
    echo "  --cleanup               Clean up test files after completion"
    echo "  --venv PATH             Path to Python virtual environment to use"
    echo "  --help                  Display this help message"
    echo
    echo "Example:"
    echo "  $0 --file /path/to/sample.mp3 --timeout 600 --cleanup"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input-bucket)
            INPUT_BUCKET="$2"
            shift 2
            ;;
        --output-bucket)
            OUTPUT_BUCKET="$2"
            shift 2
            ;;
        --file)
            SAMPLE_FILE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --venv)
            VENV_PATH="$2"
            shift 2
            ;;
        --help)
            display_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NO_COLOR}" >&2
            display_usage
            exit 1
            ;;
    esac
done

# Resolve sample file path
if [[ ! "$SAMPLE_FILE" = /* ]]; then
    # If relative path, make it relative to project root
    SAMPLE_FILE="$PROJECT_ROOT/$SAMPLE_FILE"
fi

# Check if sample file exists
if [[ ! -f "$SAMPLE_FILE" ]]; then
    echo -e "${RED}ERROR: Sample file not found: $SAMPLE_FILE${NO_COLOR}" >&2
    exit 1
fi

# Set up Python environment
echo -e "\n${BOLD}=== Preparing Video Pipeline E2E Test ===${NO_COLOR}\n"

# Activate virtual environment if specified
if [[ -n "$VENV_PATH" ]]; then
    echo -e "${YELLOW}Activating virtual environment: $VENV_PATH${NO_COLOR}"
    
    if [[ -f "$VENV_PATH/bin/activate" ]]; then
        source "$VENV_PATH/bin/activate"
    else
        echo -e "${RED}ERROR: Virtual environment not found at $VENV_PATH${NO_COLOR}" >&2
        exit 1
    fi
else
    # Try to find and activate a local venv
    for venv_dir in "$PROJECT_ROOT/venv" "$PROJECT_ROOT/.venv"; do
        if [[ -f "$venv_dir/bin/activate" ]]; then
            echo -e "${YELLOW}Activating local virtual environment: $venv_dir${NO_COLOR}"
            source "$venv_dir/bin/activate"
            break
        fi
    done
fi

# Check if boto3 is installed
python -c "import boto3" 2>/dev/null
if [[ $? -ne 0 ]]; then
    echo -e "${YELLOW}Installing test requirements...${NO_COLOR}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NO_COLOR}"
aws sts get-caller-identity > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo -e "${RED}ERROR: AWS credentials not configured or invalid${NO_COLOR}" >&2
    echo -e "${YELLOW}Please configure AWS credentials with 'aws configure' and try again${NO_COLOR}"
    exit 1
fi

# Run the Python E2E test script
echo -e "\n${BOLD}=== Running Consolidated E2E Test ===${NO_COLOR}\n"

# Build command with all parameters
CLEANUP_FLAG=""
if $CLEANUP; then
    CLEANUP_FLAG="--cleanup"
fi

SCRIPT_PATH="$SCRIPT_DIR/pipeline_e2e_test.py"
COMMAND="python $SCRIPT_PATH --input-bucket $INPUT_BUCKET --output-bucket $OUTPUT_BUCKET --sample-file \"$SAMPLE_FILE\" --timeout $TIMEOUT"

echo -e "${YELLOW}Executing: $COMMAND${NO_COLOR}"
echo

# Execute the command
eval $COMMAND
EXIT_CODE=$?

# Deactivate virtual environment if we activated one
if type deactivate &>/dev/null; then
    deactivate
fi

# Output result
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "\n${BOLD}${GREEN}Consolidated E2E Test completed successfully!${NO_COLOR}"
else
    echo -e "\n${BOLD}${RED}Consolidated E2E Test failed with exit code $EXIT_CODE${NO_COLOR}"
fi

exit $EXIT_CODE 