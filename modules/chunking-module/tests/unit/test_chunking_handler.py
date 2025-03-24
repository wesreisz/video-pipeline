import json
import pytest
from botocore.exceptions import ClientError
from handlers.chunking_handler import (
    extract_s3_details,
    process_audio_segments,
    get_s3_object,
    send_to_sqs,
    lambda_handler,
    generate_chunk_id
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
    bucket, key = extract_s3_details(sample_eventbridge_event)
    assert bucket == "test-bucket"
    assert key == "test/transcription-result.json"

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

def test_generate_chunk_id():
    """Test generation of chunk IDs."""
    # Test multiple generations to ensure format is correct
    for _ in range(10):
        chunk_id = generate_chunk_id()
        assert len(chunk_id) == 5
        assert all(c in string.ascii_uppercase + string.digits for c in chunk_id)
    
    # Test uniqueness
    chunk_ids = [generate_chunk_id() for _ in range(100)]
    assert len(set(chunk_ids)) > 95  # Allow for small chance of duplicates

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
    result = send_to_sqs(segments, "test-queue-url")
    
    # Verify the number of messages sent
    assert result == 2
    
    # Verify message format
    for msg in sent_messages:
        assert 'chunk_id' in msg
        assert len(msg['chunk_id']) == 5
        assert 'text' in msg
        assert 'start_time' in msg
        assert 'end_time' in msg

def test_send_to_sqs_failure(mocker, sample_transcription_result):
    """Test SQS message sending failure."""
    mock_sqs = mocker.patch("boto3.client")
    mock_sqs.return_value.send_message.side_effect = ClientError(
        {"Error": {"Code": "QueueDoesNotExist", "Message": "Queue not found"}},
        "send_message"
    )
    
    segments = sample_transcription_result["audio_segments"]
    with pytest.raises(ClientError):
        send_to_sqs(segments, "invalid-queue-url")

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