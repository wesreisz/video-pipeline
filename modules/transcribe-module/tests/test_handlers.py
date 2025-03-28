import unittest
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from unittest.mock import patch, MagicMock
from handlers.transcribe_handler import lambda_handler

class TestTranscribeHandler(unittest.TestCase):
    
    @patch('handlers.transcribe_handler.TranscriptionService')
    @patch('handlers.transcribe_handler.S3Utils')
    def test_lambda_handler_success_audio(self, mock_s3_utils, mock_transcription_service):
        # Setup mock returns
        mock_service_instance = MagicMock()
        mock_service_instance.process_media.return_value = 'transcriptions/audio_result.json'
        mock_transcription_service.return_value = mock_service_instance
        
        # Create test event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'audio/test.mp3'}
                }
            }]
        }
        
        # Call the handler
        response = lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['message'], 'Transcription completed successfully')
        self.assertEqual(response_body['bucket'], 'test-bucket')
        self.assertEqual(response_body['original_file'], 'audio/test.mp3')
        self.assertEqual(response_body['transcription_file'], 'transcriptions/audio_result.json')
        
        # Verify service calls
        mock_service_instance.process_media.assert_called_once_with('test-bucket', 'audio/test.mp3')

    @patch('handlers.transcribe_handler.TranscriptionService')
    @patch('handlers.transcribe_handler.S3Utils')
    def test_lambda_handler_success_video(self, mock_s3_utils, mock_transcription_service):
        # Setup mock returns
        mock_service_instance = MagicMock()
        mock_service_instance.process_media.return_value = 'transcriptions/video_result.json'
        mock_transcription_service.return_value = mock_service_instance
        
        # Create test event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'videos/test.mp4'}
                }
            }]
        }
        
        # Call the handler
        response = lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['message'], 'Transcription completed successfully')
        self.assertEqual(response_body['bucket'], 'test-bucket')
        self.assertEqual(response_body['original_file'], 'videos/test.mp4')
        self.assertEqual(response_body['transcription_file'], 'transcriptions/video_result.json')
        
        # Verify service calls
        mock_service_instance.process_media.assert_called_once_with('test-bucket', 'videos/test.mp4')
    
    def test_lambda_handler_missing_records(self):
        # Create test event with no records
        event = {'Records': []}
        
        # Call the handler
        response = lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'No records found in event') 