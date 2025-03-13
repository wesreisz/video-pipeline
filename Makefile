.PHONY: start-localstack stop-localstack test-local unit-tests

# Default Python interpreter
PYTHON=python3

# Directory structure
TEST_DIR=projects/transcribe-module/tests
SRC_DIR=projects/transcribe-module/src
SAMPLE_DIR=samples

# Start LocalStack in a Docker container
start-localstack:
	@echo "Starting LocalStack container..."
	docker run -d --name localstack \
		-p 4566:4566 -p 4510-4559:4510-4559 \
		-e SERVICES=s3,lambda \
		-e DEBUG=1 \
		-e DATA_DIR=/tmp/localstack/data \
		localstack/localstack

# Stop and remove LocalStack container
stop-localstack:
	@echo "Stopping LocalStack container..."
	-docker stop localstack
	-docker rm localstack

# Run unit tests
unit-tests:
	@echo "Running unit tests..."
	cd $(TEST_DIR)/.. && $(PYTHON) -m unittest discover tests

# Run local integration test with LocalStack
test-local:
	@echo "Running local integration test with LocalStack..."
	cd projects/transcribe-module && $(PYTHON) local_test.py

# Create sample audio file if it doesn't exist
create-sample:
	@echo "Creating sample directory and audio file..."
	mkdir -p $(SAMPLE_DIR)
	@if [ ! -f $(SAMPLE_DIR)/sample.mp3 ]; then \
		echo "Creating dummy sample.mp3 file..."; \
		echo "DUMMY AUDIO DATA" > $(SAMPLE_DIR)/sample.mp3; \
	else \
		echo "Sample file already exists."; \
	fi

# Clean up generated files
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

# Setup development environment
setup-dev: create-sample
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	pip install pytest pytest-cov localstack awscli-local

# Run the full local test workflow
test-workflow: stop-localstack start-localstack create-sample test-local stop-localstack

# Help
help:
	@echo "Available commands:"
	@echo "  make setup-dev        - Set up development environment"
	@echo "  make start-localstack - Start LocalStack container"
	@echo "  make stop-localstack  - Stop LocalStack container"
	@echo "  make create-sample    - Create sample audio file"
	@echo "  make unit-tests       - Run unit tests"
	@echo "  make test-local       - Run local test with LocalStack"
	@echo "  make test-workflow    - Run full test workflow"
	@echo "  make clean            - Clean up generated files"

# Default target
all: help 