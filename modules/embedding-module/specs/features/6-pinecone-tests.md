# Pinecone Integration Tests

This document outlines the testing requirements for the Pinecone vector database integration. Follow the project's pytest standards defined in `.cursor/rules/pytest.mdc`.

## Test Coverage Requirements

### 1. Mock-Based Integration Tests

Implement comprehensive mock-based tests that verify:

- Service initialization and configuration
  * Proper API key handling using new `Pinecone()` class
  * Environment configuration
  * Index name configuration
  * Index existence checking
  * **IMPORTANT**: Mock the Pinecone client at `services.pinecone_service.Pinecone` path, not at `pinecone.Pinecone`

- Index Management
  * Auto-creation of non-existent indexes
  * Proper serverless configuration with required parameters:
    - `cloud="aws"`
    - `region` matching the environment (e.g., "us-east-1")
  * Correct dimension and metric settings
  * Proper use of `ServerlessSpec` for index creation

- Upsert Operations
  * Vector data formatting according to new API requirements
  * Metadata structure validation
  * Response handling
  * Namespace support
  * Storage status verification after each upsert operation
  * Proper mocking of `describe_index_stats` response

- Error Handling
  * API errors
  * Configuration errors
  * Input validation
  * Missing credentials
  * JSON serialization handling

### 2. Live API Tests

Implement optional live API tests that:
- Can be enabled via `RUN_LIVE_TESTS=1`
- Verify actual Pinecone service interaction
- Follow free-tier limitations
- Clean up test data when possible

## Mock Setup Requirements

### 1. Mock Index Creation

Create a function that returns a mock Pinecone index with:
- Proper upsert response format for the new API (dictionary with upserted_count)
- Mocked describe_index_stats response with namespaces, dimension, and total_vector_count
- All necessary mock methods for index operations

### 2. Mock Pinecone Client

Create a fixture that:
- Properly mocks the Pinecone client class
- Sets up mock responses for list_indexes, create_index, and Index methods
- Uses the correct patching path for the new API
- Returns a properly configured mock client

### 3. Mock Secrets Service

Create a fixture that:
- Provides mock responses for all required configuration methods
- Returns appropriate test values for API key, environment, and index name
- Handles both successful and error scenarios

## Service Implementation Requirements

### 1. Service Initialization

The service initialization should:
- Handle optional SecretsService injection for testing
- Validate required credentials
- Use default values for optional configuration
- Initialize the Pinecone client with the new API
- Set up proper error handling and logging
- Create or verify index existence

### 2. Storage Status Verification

Implement storage status verification that:
- Checks index stats after each upsert operation
- Logs total vector count and dimension
- Handles missing or invalid stats gracefully
- Provides proper error reporting

### 3. ServerlessSpec Configuration

Ensure index creation:
- Uses the correct ServerlessSpec parameters
- Configures cloud and region properly
- Sets correct dimension and metric values
- Handles creation errors appropriately

## Test Cases

### Required Test Scenarios

1. Service Initialization
   - Successful initialization with all parameters
   - Initialization with default values
   - Handling of missing credentials
   - Proper client setup verification

2. Upsert Operations
   - Successful vector upsert with complete metadata including text content
   - Verification of text field preservation in metadata
   - Storage status verification
   - Error handling for invalid inputs
   - Proper response validation
   - Handling of optional metadata fields (original_file, segment_id)
   - Validation of text content formatting and storage

3. Live API Testing
   - Initial state capture
   - Vector upsert verification with complete metadata
   - Text content retrieval and validation
   - Storage status validation
   - Proper test data cleanup
   - Only run test if RUN_LIVE_TESTS is set

## Package Version Requirements

The tests must work with:
- `pinecone==6.0.2` in `requirements.txt`
- No additional type stubs (types-pinecone should be removed)

### Version-Specific Requirements

1. Package Name
   - Use `pinecone` package
   - Avoid deprecated `pinecone-client`

2. Client Initialization
   - Use new client-based initialization
   - Avoid deprecated global initialization

3. ServerlessSpec Configuration
   - Include required cloud and region parameters
   - Use proper configuration structure

4. Import Requirements
   - Use new import structure
   - Avoid deprecated imports
   - Import only necessary components

## Test Execution Requirements

Tests should be runnable using:
- Standard test execution with mock dependencies
- Optional live API testing with environment variable
- Coverage reporting for service implementation

## Expected Coverage

The test suite should achieve:
- ~95% coverage of the Pinecone service implementation
- Full coverage of critical paths
- Proper verification of all operations

## Test Organization

Organize tests in `tests/integration/test_pinecone_service_integration.py` with:

1. Required Fixtures
   - Pinecone client mock
   - SecretsService mock
   - Test data generation
   - Storage verification utilities

2. Test Categories
   - Service initialization
   - Index management
   - Upsert operations
   - Error scenarios
   - Input validation
   - JSON handling

## Dependencies

- Remove `types-pinecone` from dev-requirements.txt
- Ensure all other test dependencies are properly specified
- Use appropriate versions for all dependencies

## Best Practices

1. Test Structure
   - Use descriptive test names
   - Include proper docstrings
   - Focus on behavior testing
   - Maintain test independence

2. Mock Configuration
   - Use correct mock hierarchy
   - Provide appropriate return values
   - Handle all required scenarios
   - Validate mock interactions

3. Error Handling
   - Test all error conditions
   - Verify error messages
   - Ensure proper cleanup
   - Handle edge cases

4. Data Validation
   - Verify response formats
   - Validate metadata handling
   - Check storage status
   - Confirm proper cleanup

### Mock Data Requirements

1. Test Vector Data
   ```python
   MOCK_METADATA = TalkMetadata(
       speaker=["John Doe"],
       start_time="10.500",
       end_time="20.750",
       title="Test Talk",
       track="Test Track",
       day="2024-03-20",
       text="This is a test chunk",
       original_file="test.mp3",
       segment_id="segment_1"
   )
   ```

2. Expected Vector Format
   ```python
   expected_vector_data = [(
       "test_chunk_1",
       MOCK_VECTOR,
       {
           "speaker": ["John Doe"],
           "start_time": "10.500",
           "end_time": "20.750",
           "title": "Test Talk",
           "track": "Test Track",
           "day": "2024-03-20",
           "text": "This is a test chunk",
           "original_file": "test.mp3",
           "segment_id": "segment_1"
       }
   )]
   ``` 