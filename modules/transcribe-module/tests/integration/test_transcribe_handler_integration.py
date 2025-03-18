import unittest
import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from handlers.transcribe_handler import lambda_handler

class TestTranscribeHandlerIntegration(unittest.TestCase):
    """Integration tests for the transcribe handler Lambda function"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures before each test"""
        # Create mock instances that will be used across tests
        self.mock_s3_utils_instance = MagicMock()
        self.mock_transcription_service_instance = MagicMock()
        
        # Configure default timestamp for consistency
        self.mock_s3_utils_instance.get_current_timestamp.return_value = "2023-03-16T12:00:00.000000"
        
        # Setup patchers
        self.s3_utils_patcher = patch('handlers.transcribe_handler.S3Utils')
        self.transcription_service_patcher = patch('handlers.transcribe_handler.TranscriptionService')
        
        # Start patchers and get mocks
        self.mock_s3_utils = self.s3_utils_patcher.start()
        self.mock_transcription_service = self.transcription_service_patcher.start()
        
        # Configure mocks to return our instances
        self.mock_s3_utils.return_value = self.mock_s3_utils_instance
        self.mock_transcription_service.return_value = self.mock_transcription_service_instance
        
        # Yield for test execution
        yield
        
        # Stop patchers after test
        self.s3_utils_patcher.stop()
        self.transcription_service_patcher.stop()
    
    def test_valid_s3_event_audio_success(self):
        """Test successful transcription flow with an audio file"""
        # Arrange
        output_key = "transcriptions/sample-audio.json"
        self.mock_transcription_service_instance.process_media.return_value = output_key
        
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'input-bucket'},
                    'object': {'key': 'audio/sample-audio.mp3'}
                }
            }]
        }
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Transcription completed successfully')
        self.assertEqual(body['bucket'], 'input-bucket')
        self.assertEqual(body['original_file'], 'audio/sample-audio.mp3')
        self.assertEqual(body['transcription_file'], output_key)
        
        # Verify service interactions
        self.mock_transcription_service_instance.process_media.assert_called_once_with(
            'input-bucket', 'audio/sample-audio.mp3'
        )
    
    def test_valid_s3_event_video_success(self):
        """Test successful transcription flow with a video file"""
        # Arrange
        output_key = "transcriptions/sample-video.json"
        self.mock_transcription_service_instance.process_media.return_value = output_key
        
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'input-bucket'},
                    'object': {'key': 'videos/sample-video.mp4'}
                }
            }]
        }
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Transcription completed successfully')
        self.assertEqual(body['bucket'], 'input-bucket')
        self.assertEqual(body['original_file'], 'videos/sample-video.mp4')
        self.assertEqual(body['transcription_file'], output_key)
        
        # Verify service interactions
        self.mock_transcription_service_instance.process_media.assert_called_once_with(
            'input-bucket', 'videos/sample-video.mp4'
        )
    
    def test_missing_records(self):
        """Test handling of event with no records"""
        # Arrange
        event = {'Records': []}
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'No records found in event')
        
        # Verify no service interactions
        self.mock_transcription_service_instance.process_media.assert_not_called()
    
    def test_empty_event(self):
        """Test handling of empty event (no Records key)"""
        # Arrange
        event = {}
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'No records found in event')
        
        # Verify no service interactions
        self.mock_transcription_service_instance.process_media.assert_not_called()
    
    def test_missing_bucket_info(self):
        """Test handling of event with missing bucket information"""
        # Arrange
        event = {
            'Records': [{
                's3': {
                    'object': {'key': 'audio/sample.mp3'}
                    # Missing bucket
                }
            }]
        }
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Missing bucket or key information')
        
        # Verify no service interactions
        self.mock_transcription_service_instance.process_media.assert_not_called()
    
    def test_missing_key_info(self):
        """Test handling of event with missing key information"""
        # Arrange
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'input-bucket'}
                    # Missing object/key
                }
            }]
        }
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Missing bucket or key information')
        
        # Verify no service interactions
        self.mock_transcription_service_instance.process_media.assert_not_called()
    
    def test_transcription_service_exception(self):
        """Test handling of exception from transcription service"""
        # Arrange
        self.mock_transcription_service_instance.process_media.side_effect = Exception("Transcription failed")
        
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'input-bucket'},
                    'object': {'key': 'audio/sample.mp3'}
                }
            }]
        }
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        # Update to match the actual error_handler.py implementation
        self.assertEqual(body['error'], 'Transcription failed')
        self.assertEqual(body['message'], 'Error processing transcription request')
        
        # Verify service interactions
        self.mock_transcription_service_instance.process_media.assert_called_once_with(
            'input-bucket', 'audio/sample.mp3'
        )
    
    def test_malformed_s3_event(self):
        """Test handling of malformed S3 event"""
        # Arrange
        event = {
            'Records': [{
                # Missing s3 key
                'eventSource': 's3'
            }]
        }
        
        # Act
        response = lambda_handler(event, {})
        
        # Assert
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Missing bucket or key information')
        
        # Verify no service interactions
        self.mock_transcription_service_instance.process_media.assert_not_called()

if __name__ == '__main__':
    unittest.main() 