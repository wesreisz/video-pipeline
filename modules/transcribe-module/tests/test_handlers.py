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
        
        # Setup S3Utils mock to return empty metadata
        mock_s3_utils_instance = MagicMock()
        mock_s3_utils_instance.get_object_metadata.return_value = {}
        mock_s3_utils.return_value = mock_s3_utils_instance
        
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
        
        # Verify empty metadata is handled gracefully
        self.assertIn('metadata', response_body)
        self.assertEqual(response_body['metadata'], {})
        
        # Verify service calls
        mock_s3_utils_instance.get_object_metadata.assert_called_once_with('test-bucket', 'audio/test.mp3')
        mock_service_instance.process_media.assert_called_once_with('test-bucket', 'audio/test.mp3')

    @patch('handlers.transcribe_handler.TranscriptionService')
    @patch('handlers.transcribe_handler.S3Utils')
    def test_lambda_handler_success_video(self, mock_s3_utils, mock_transcription_service):
        # Setup mock returns
        mock_service_instance = MagicMock()
        mock_service_instance.process_media.return_value = 'transcriptions/video_result.json'
        mock_transcription_service.return_value = mock_service_instance
        
        # Setup S3Utils mock to return empty metadata
        mock_s3_utils_instance = MagicMock()
        mock_s3_utils_instance.get_object_metadata.return_value = {}
        mock_s3_utils.return_value = mock_s3_utils_instance
        
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
        
        # Verify empty metadata is handled gracefully
        self.assertIn('metadata', response_body)
        self.assertEqual(response_body['metadata'], {})
        
        # Verify service calls
        mock_s3_utils_instance.get_object_metadata.assert_called_once_with('test-bucket', 'videos/test.mp4')
        mock_service_instance.process_media.assert_called_once_with('test-bucket', 'videos/test.mp4')
    
    def test_lambda_handler_missing_records(self):
        # Create test event with no records
        event = {'Records': []}
        
        # Call the handler
        response = lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'No records found in event')

    @patch('handlers.transcribe_handler.TranscriptionService')
    @patch('handlers.transcribe_handler.S3Utils')
    def test_lambda_handler_with_metadata(self, mock_s3_utils, mock_transcription_service):
        # Setup mock returns
        mock_service_instance = MagicMock()
        mock_service_instance.process_media.return_value = 'transcriptions/test_with_metadata.json'
        mock_transcription_service.return_value = mock_service_instance
        
        # Setup S3Utils mock to return metadata
        mock_s3_utils_instance = MagicMock()
        mock_s3_utils_instance.get_object_metadata.return_value = {
            'speaker': 'John Doe',
            'title': 'Test Talk',
            'track': 'Technical Track',
            'day': 'Monday'
        }
        mock_s3_utils.return_value = mock_s3_utils_instance
        
        # Create test event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'test/file.mp4'}
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
        self.assertEqual(response_body['original_file'], 'test/file.mp4')
        
        # Verify metadata in response
        self.assertIn('metadata', response_body)
        metadata = response_body['metadata']
        self.assertEqual(metadata['speaker'], 'John Doe')
        self.assertEqual(metadata['title'], 'Test Talk')
        self.assertEqual(metadata['track'], 'Technical Track')
        self.assertEqual(metadata['day'], 'Monday')
        
        # Verify metadata in EventBridge format
        self.assertIn('metadata', response['detail']['records'][0])
        event_metadata = response['detail']['records'][0]['metadata']
        self.assertEqual(event_metadata, metadata)
        
        # Verify service calls
        mock_s3_utils_instance.get_object_metadata.assert_called_once_with('test-bucket', 'test/file.mp4')
        mock_service_instance.process_media.assert_called_once_with('test-bucket', 'test/file.mp4')

    @patch('handlers.transcribe_handler.TranscriptionService')
    @patch('handlers.transcribe_handler.S3Utils')
    def test_lambda_handler_without_metadata(self, mock_s3_utils, mock_transcription_service):
        # Setup mock returns
        mock_service_instance = MagicMock()
        mock_service_instance.process_media.return_value = 'transcriptions/test_without_metadata.json'
        mock_transcription_service.return_value = mock_service_instance
        
        # Setup S3Utils mock to return empty metadata
        mock_s3_utils_instance = MagicMock()
        mock_s3_utils_instance.get_object_metadata.return_value = {}
        mock_s3_utils.return_value = mock_s3_utils_instance
        
        # Create test event
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'test/file.mp4'}
                }
            }]
        }
        
        # Call the handler
        response = lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['message'], 'Transcription completed successfully')
        
        # Verify empty metadata is handled gracefully
        self.assertIn('metadata', response_body)
        self.assertEqual(response_body['metadata'], {})
        
        # Verify empty metadata in EventBridge format
        self.assertIn('metadata', response['detail']['records'][0])
        self.assertEqual(response['detail']['records'][0]['metadata'], {})
        
        # Verify service calls
        mock_s3_utils_instance.get_object_metadata.assert_called_once_with('test-bucket', 'test/file.mp4')
        mock_service_instance.process_media.assert_called_once_with('test-bucket', 'test/file.mp4') 