import json
import pytest
from botocore.exceptions import ClientError
from handlers.chunking_handler import (
    extract_s3_details,
    process_audio_segments,
    get_s3_object,
    send_to_sqs,
    lambda_handler,
    generate_chunk_hash
)
import string

@pytest.fixture
def sample_eventbridge_event():
    """Sample EventBridge event with S3 details."""
    return {
        "detail": {
            "records": [{
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "test/transcription-result.json"}
                }
            }]
        }
    }

@pytest.fixture
def sample_transcription_result():
    """Return a sample transcription result."""
    return {
        "transcription_text": "This is a test transcription.",
        "audio_segments": [
            {
                "id": 0,
                "transcript": "This is the first test segment.",
                "start_time": "0.0",
                "end_time": "10.0",
                "items": [0, 1, 2, 3, 4]
            },
            {
                "id": 1,
                "transcript": "This is the second test segment.",
                "start_time": "10.0",
                "end_time": "20.0",
                "items": [5, 6, 7, 8, 9]
            }
        ]
    }

def test_extract_s3_details_valid_event(sample_eventbridge_event):
    """Test extracting S3 details from a valid EventBridge event."""
    bucket, key, metadata = extract_s3_details(sample_eventbridge_event)
    assert bucket == "test-bucket"
    assert key == "test/transcription-result.json"
    assert isinstance(metadata, dict)

def test_extract_s3_details_missing_detail():
    """Test extracting S3 details from event without detail."""
    result = extract_s3_details({})
    assert result is None

def test_extract_s3_details_missing_records():
    """Test extracting S3 details from event without records."""
    result = extract_s3_details({"detail": {}})
    assert result is None

def test_process_audio_segments_valid(sample_transcription_result):
    """Test processing valid audio segments."""
    result = process_audio_segments(sample_transcription_result)
    assert len(result) == 2
    assert all(isinstance(segment, dict) for segment in result)
    assert all("start_time" in segment and "end_time" in segment for segment in result)

def test_process_audio_segments_empty():
    """Test processing empty segment list."""
    result = process_audio_segments({"audio_segments": []})
    assert result == []

def test_process_audio_segments_missing_segments():
    """Test processing data with missing segments."""
    result = process_audio_segments({})
    assert result == []

def test_process_audio_segments_old_format():
    """Test processing data in old format."""
    old_format = {
        "results": {
            "segments": [
                {
                    "start_time": 0.0,
                    "end_time": 10.0,
                    "text": "This is a test."
                }
            ]
        }
    }
    result = process_audio_segments(old_format)
    assert len(result) == 1
    assert result[0]["start_time"] == 0.0
    assert result[0]["end_time"] == 10.0

def test_get_s3_object_success(mocker, mock_s3_response, sample_transcription_result):
    """Test successful S3 object retrieval."""
    mock_s3 = mocker.patch("boto3.client")
    mock_s3.return_value.get_object.return_value = mock_s3_response
    
    result = get_s3_object("test-bucket", "test-key")
    assert result == sample_transcription_result

def test_get_s3_object_not_found(mocker):
    """Test S3 object not found."""
    mock_s3 = mocker.patch("boto3.client")
    mock_s3.return_value.get_object.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
        "get_object"
    )
    
    with pytest.raises(ValueError, match="File test-key not found in bucket test-bucket"):
        get_s3_object("test-bucket", "test-key")

def test_get_s3_object_invalid_json(mocker):
    """Test invalid JSON in S3 object."""
    class MockBody:
        def read(self):
            return b'invalid json'
    
    mock_response = {'Body': MockBody()}
    mock_s3 = mocker.patch("boto3.client")
    mock_s3.return_value.get_object.return_value = mock_response
    
    with pytest.raises(ValueError, match="File test-key is not valid JSON"):
        get_s3_object("test-bucket", "test-key")

def test_generate_chunk_hash():
    """Test generation of chunk hashes."""
    # Test that hashes are deterministic
    original_file = "test_file.mp3"
    segment_id = 1
    
    hash1 = generate_chunk_hash(original_file, segment_id)
    hash2 = generate_chunk_hash(original_file, segment_id)
    assert hash1 == hash2
    
    # Test different inputs produce different hashes
    hash3 = generate_chunk_hash(original_file, 2)
    assert hash1 != hash3
    
    # Test input validation
    with pytest.raises(ValueError):
        generate_chunk_hash("", 1)
    with pytest.raises(ValueError):
        generate_chunk_hash(original_file, -1)

def test_send_to_sqs_success(mocker, sample_transcription_result):
    """Test successful SQS message sending."""
    mock_sqs = mocker.patch("boto3.client")
    mock_sqs.return_value.send_message.return_value = {
        'MessageId': 'test_message_id_1'
    }
    
    # Capture the messages being sent
    sent_messages = []
    def mock_send_message(**kwargs):
        sent_messages.append(json.loads(kwargs['MessageBody']))
        return {'MessageId': 'test_message_id_1'}
    
    mock_sqs.return_value.send_message.side_effect = mock_send_message
    
    segments = sample_transcription_result["audio_segments"]
    test_metadata = {"title": "Test Video", "author": "Test Author"}
    result = send_to_sqs(segments, "test-file.mp3", test_metadata)
    
    # Verify the number of messages sent
    assert result == 2
    
    # Verify message format
    for msg in sent_messages:
        assert 'chunk_id' in msg
        # Hash should be exactly 10 characters
        assert len(msg['chunk_id']) == 10
        assert all(c in '0123456789abcdef' for c in msg['chunk_id'])
        assert 'text' in msg
        assert 'start_time' in msg
        assert 'end_time' in msg
        assert 'original_file' in msg
        assert 'segment_id' in msg
        assert 'metadata' in msg
        assert msg['metadata'] == test_metadata

def test_send_to_sqs_failure(mocker, sample_transcription_result):
    """Test SQS message sending failure."""
    mock_sqs = mocker.patch("boto3.client")
    mock_sqs.return_value.send_message.side_effect = ClientError(
        {"Error": {"Code": "QueueDoesNotExist", "Message": "Queue not found"}},
        "send_message"
    )
    
    segments = sample_transcription_result["audio_segments"]
    test_metadata = {"title": "Test Video"}
    with pytest.raises(ClientError):
        send_to_sqs(segments, "test-file.mp3", test_metadata, "invalid-queue-url")

def test_lambda_handler_success(mocker, sample_eventbridge_event, sample_transcription_result):
    """Test successful end-to-end lambda execution."""
    mock_s3 = mocker.patch("handlers.chunking_handler.get_s3_object")
    mock_s3.return_value = sample_transcription_result
    
    mock_sqs = mocker.patch("handlers.chunking_handler.send_to_sqs")
    mock_sqs.return_value = 2
    
    result = lambda_handler(sample_eventbridge_event, {})
    assert result["statusCode"] == 200
    assert json.loads(result["body"])["segments_sent"] == 2

def test_lambda_handler_invalid_event():
    """Test lambda handler with invalid event."""
    result = lambda_handler({"detail": {}}, {})
    assert result["statusCode"] == 200
    assert "No records to process" in json.loads(result["body"])["message"] 