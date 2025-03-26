import os
import pytest
from unittest.mock import patch, MagicMock
from typing import List, Dict
import pinecone
from dataclasses import dataclass
import logging

from services.pinecone_service import (
    PineconeService,
    PineconeServiceError,
    UpsertResponse,
    TalkMetadata
)

# Mock data
MOCK_VECTOR = [0.1] * 1536  # OpenAI's ada-002 produces 1536-dimensional vectors
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

@dataclass
class MockIndexStats:
    """Mock for Pinecone index statistics."""
    total_vector_count: int = 0
    dimension: int = 1536
    namespaces: Dict[str, Dict] = None

def create_mock_index():
    """Create a mock Pinecone index with proper response formats."""
    mock_index = MagicMock()
    
    # Configure mock responses
    mock_index.upsert.return_value = None  # Pinecone upsert doesn't return meaningful data
    mock_index.describe_index_stats.return_value = MockIndexStats(
        total_vector_count=1,
        dimension=1536,
        namespaces={"": {"vector_count": 1}}
    )
    
    return mock_index

@pytest.fixture(autouse=True)
def mock_pinecone_base(mocker):
    """Mock base Pinecone components to prevent live API calls."""
    # Create mock objects
    mock_index = mocker.MagicMock()
    mock_client = mocker.MagicMock()
    mock_index_api = mocker.MagicMock()
    mock_stats = mocker.MagicMock()
    
    # Configure mock stats
    mock_stats.total_vector_count = 0
    mock_stats.dimension = 1536
    
    # Configure mock index
    mock_index.describe_index_stats.return_value = mock_stats
    mock_index.upsert.return_value = None
    
    # Configure mock client
    mock_client.Index.return_value = mock_index
    mock_client.list_indexes.return_value = []
    
    # Mock the Pinecone class
    mock_pinecone_class = mocker.patch('services.pinecone_service.Pinecone')
    mock_pinecone_class.return_value = mock_client
    
    # Mock ServerlessSpec and CloudProvider
    mock_serverless_spec = mocker.patch('services.pinecone_service.ServerlessSpec')
    mock_cloud_provider = mocker.patch('services.pinecone_service.CloudProvider')
    mock_cloud_provider.AWS = 'aws'
    
    # Return all mocks for use in tests
    return {
        'client': mock_client,
        'index': mock_index,
        'stats': mock_stats,
        'Pinecone': mock_pinecone_class,
        'ServerlessSpec': mock_serverless_spec,
        'CloudProvider': mock_cloud_provider
    }

@pytest.fixture
def mock_pinecone(mocker):
    """Create a mock Pinecone client using the new v6.0.2 API."""
    # Create mock objects
    mock_index = mocker.MagicMock()
    mock_client = mocker.MagicMock()
    mock_stats = MockIndexStats(total_vector_count=1)
    
    # Configure mock index
    mock_index.describe_index_stats.return_value = mock_stats
    mock_index.upsert.return_value = None
    
    # Configure mock client
    mock_client.Index.return_value = mock_index
    mock_client.list_indexes.return_value = [mocker.MagicMock(name="talk-embeddings")]
    
    # Mock the Pinecone class
    mock_pinecone_class = mocker.patch('services.pinecone_service.Pinecone')
    mock_pinecone_class.return_value = mock_client
    
    # Mock ServerlessSpec and CloudProvider
    mock_serverless_spec = mocker.patch('services.pinecone_service.ServerlessSpec')
    mock_cloud_provider = mocker.patch('services.pinecone_service.CloudProvider')
    mock_cloud_provider.AWS = 'aws'
    
    # Return all mocks for use in tests
    return {
        'client': mock_client,
        'index': mock_index,
        'stats': mock_stats,
        'Pinecone': mock_pinecone_class,
        'ServerlessSpec': mock_serverless_spec,
        'CloudProvider': mock_cloud_provider
    }

@pytest.fixture
def mock_secrets_service():
    """Create a mock SecretsService."""
    mock_service = MagicMock()
    mock_service.get_pinecone_api_key.return_value = "mock-api-key"
    mock_service.get_pinecone_environment.return_value = "us-east-1"
    mock_service.get_pinecone_index_name.return_value = "talk-embeddings"
    return mock_service

@pytest.fixture
def pinecone_service(mock_pinecone, mock_secrets_service):
    """Create a PineconeService instance with mocked dependencies."""
    return PineconeService(secrets_service=mock_secrets_service)

@pytest.mark.integration
def test_mocked_service_initialization(mock_pinecone, mock_secrets_service):
    """Test service initialization with mocked dependencies."""
    service = PineconeService(secrets_service=mock_secrets_service)
    
    # Verify Pinecone client was initialized correctly
    mock_pinecone['Pinecone'].assert_called_once_with(api_key="mock-api-key")
    
    # Verify index existence was checked
    mock_pinecone['client'].list_indexes.assert_called_once()
    
    # Verify index was retrieved
    mock_pinecone['client'].Index.assert_called_once_with("talk-embeddings")
    
    # Verify storage status was checked
    mock_pinecone['index'].describe_index_stats.assert_called_once()

@pytest.mark.integration
def test_mocked_upsert_embeddings(mock_pinecone, mock_secrets_service):
    """Test upserting embeddings with mocked Pinecone."""
    # Setup
    service = PineconeService(secrets_service=mock_secrets_service)
    
    # Create test data
    vectors = [MOCK_VECTOR]
    ids = ["test_chunk_1"]
    metadata = [MOCK_METADATA]
    
    # Configure mock stats to show updated vector count
    mock_pinecone['index'].describe_index_stats.return_value.total_vector_count = 1
    
    # Perform upsert
    response = service.upsert_embeddings(vectors, ids, metadata)
    
    # Verify upsert was called with correct data
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
    mock_pinecone['index'].upsert.assert_called_once_with(
        vectors=expected_vector_data,
        namespace=None
    )
    
    # Verify response
    assert response.upserted_count == 1
    assert response.total_vector_count == 1

@pytest.mark.integration
def test_mocked_index_creation(mock_pinecone, mock_secrets_service):
    """Test index creation with mocked Pinecone."""
    # Configure mock to indicate index doesn't exist
    mock_pinecone['client'].list_indexes.return_value = []
    
    # Setup
    service = PineconeService(secrets_service=mock_secrets_service)
    
    # Verify create_index was called with correct parameters
    mock_pinecone['client'].create_index.assert_called_once_with(
        name="talk-embeddings",
        dimension=1536,
        metric="cosine",
        spec=mock_pinecone['ServerlessSpec'].return_value
    )
    
    # Verify ServerlessSpec was called correctly
    mock_pinecone['ServerlessSpec'].assert_called_once_with(
        cloud=mock_pinecone['CloudProvider'].AWS,
        region="us-east-1"
    )

@pytest.mark.integration
def test_mocked_error_handling(pinecone_service):
    """Test handling of Pinecone errors."""
    # Configure mock to raise an error
    pinecone_service.index.upsert.side_effect = Exception("Pinecone API error")
    
    # Test error handling
    with pytest.raises(PineconeServiceError, match="Error upserting vectors: Pinecone API error"):
        pinecone_service.upsert_embeddings(
            vectors=[MOCK_VECTOR],
            ids=["test_chunk_1"],
            metadata=[MOCK_METADATA]
        )

@pytest.mark.integration
def test_storage_status_verification(pinecone_service):
    """Test storage status verification functionality."""
    # Configure mock with incorrect dimension
    pinecone_service.index.describe_index_stats.return_value = MockIndexStats(
        total_vector_count=1,
        dimension=512  # Wrong dimension
    )
    
    # Test dimension mismatch error
    with pytest.raises(PineconeServiceError, match="Index dimension mismatch"):
        pinecone_service._verify_storage_status()
    
    # Configure mock with correct dimension but API error
    pinecone_service.index.describe_index_stats.side_effect = Exception("API Error")
    
    # Test API error handling
    with pytest.raises(PineconeServiceError, match="Error verifying storage status"):
        pinecone_service._verify_storage_status()

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv('RUN_LIVE_TESTS'), reason="Live API tests are disabled")
def test_live_api_upsert():
    """
    Test upserting embeddings using the live Pinecone API.
    This test is skipped by default and only runs when RUN_LIVE_TESTS is set.
    
    To run this test:
    1. Set RUN_LIVE_TESTS=1
    2. Ensure PINECONE_API_KEY is set in environment or secrets
    3. Optional: Set PINECONE_ENVIRONMENT and PINECONE_INDEX_NAME
    """
    # Create service without mocks to use real API
    service = PineconeService()
    test_id = "test_chunk_live"
    
    try:
        # Test data
        vectors = [MOCK_VECTOR]
        ids = [test_id]
        metadata = [MOCK_METADATA]
        
        # Perform upsert
        response = service.upsert_embeddings(
            vectors=vectors,
            ids=ids,
            metadata=metadata
        )
        
        # Verify response structure
        assert isinstance(response, UpsertResponse)
        assert response.upserted_count == 1
        assert isinstance(response.namespace, (str, type(None)))
        assert isinstance(response.total_vector_count, int)
        assert response.total_vector_count > 0
        
    finally:
        # Clean up test data
        try:
            # Ensure cleanup happens even if assertions fail
            if service and service.index:
                service.index.delete(ids=[test_id])
                # Verify deletion
                stats = service.index.describe_index_stats()
                logger.info(f"Cleanup completed. Total vectors after cleanup: {stats.total_vector_count}")
        except Exception as e:
            logger.warning(f"Error during test cleanup: {str(e)}")
            # Don't raise the cleanup error as it might mask the actual test failure
            pass

@pytest.mark.integration
def test_mocked_input_validation(pinecone_service):
    """Test input validation for upsert operation."""
    # Test empty vectors
    with pytest.raises(PineconeServiceError, match="Invalid input for upsert operation: Vectors, IDs, and metadata lists cannot be empty"):
        pinecone_service.upsert_embeddings([], [], [])
    
    # Test mismatched lengths
    with pytest.raises(PineconeServiceError, match="Invalid input for upsert operation: Vectors, IDs, and metadata lists must have the same length"):
        pinecone_service.upsert_embeddings(
            vectors=[MOCK_VECTOR],
            ids=["id1", "id2"],
            metadata=[MOCK_METADATA]
        ) 