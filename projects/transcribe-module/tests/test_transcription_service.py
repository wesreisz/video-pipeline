import unittest
import os
import json
from unittest.mock import MagicMock, patch
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.transcription_service import TranscriptionService
from models.transcription_result import TranscriptionResult

class TestTranscriptionService(unittest.TestCase):
    
    def setUp(self):
        self.service = TranscriptionService()
        self.service.s3_utils = MagicMock()
        self.service.transcribe_client = MagicMock()
        self.service.output_bucket = 'test-output-bucket'
    
    @patch('boto3.client')
    def test_process_audio_legacy(self, mock_boto_client):
        """Test that the legacy process_audio method calls process_media"""
        # Setup mock
        self.service.process_media = MagicMock(return_value='transcriptions/test_audio.json')
        
        # Call the legacy method
        result = self.service.process_audio('test-bucket', 'audio/test_audio.mp3')
        
        # Verify it calls the new method
        self.service.process_media.assert_called_once_with('test-bucket', 'audio/test_audio.mp3')
        self.assertEqual(result, 'transcriptions/test_audio.json')
    
    @patch('time.sleep', return_value=None)
    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_audio(self, mock_uuid, mock_sleep):
        """Test processing an audio file"""
        # Setup mocks
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._wait_for_transcription = MagicMock(return_value="This is a test transcription")
        
        # Mock the transcription job response
        self.service.transcribe_client.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }
        
        # Call the method being tested
        result = self.service.process_media('test-bucket', 'audio/test_audio.mp3')
        
        # Assertions
        self.service.transcribe_client.start_transcription_job.assert_called_once()
        
        # Check that the correct arguments were passed
        call_args = self.service.transcribe_client.start_transcription_job.call_args[1]
        self.assertEqual(call_args['TranscriptionJobName'], 'transcribe-test-uuid')
        self.assertEqual(call_args['Media']['MediaFileUri'], 's3://test-bucket/audio/test_audio.mp3')
        self.assertEqual(call_args['MediaFormat'], 'mp3')
        
        # Check the upload to S3
        expected_dict = {
            'original_file': 'audio/test_audio.mp3',
            'transcription_text': 'This is a test transcription',
            'timestamp': '2023-04-01T12:00:00',
            'job_name': 'transcribe-test-uuid',
            'media_type': 'audio'
        }
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_audio.json', expected_dict)
        
        self.assertEqual(result, 'transcriptions/test_audio.json')

    @patch('time.sleep', return_value=None)
    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_video(self, mock_uuid, mock_sleep):
        """Test processing a video file"""
        # Setup mocks
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._wait_for_transcription = MagicMock(return_value="This is a test video transcription")
        
        # Mock the transcription job response
        self.service.transcribe_client.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }
        
        # Call the method being tested
        result = self.service.process_media('test-bucket', 'videos/test_video.mp4')
        
        # Assertions
        self.service.transcribe_client.start_transcription_job.assert_called_once()
        
        # Check that the correct arguments were passed
        call_args = self.service.transcribe_client.start_transcription_job.call_args[1]
        self.assertEqual(call_args['TranscriptionJobName'], 'transcribe-test-uuid')
        self.assertEqual(call_args['Media']['MediaFileUri'], 's3://test-bucket/videos/test_video.mp4')
        self.assertEqual(call_args['MediaFormat'], 'mp4')
        
        # Check the upload to S3
        expected_dict = {
            'original_file': 'videos/test_video.mp4',
            'transcription_text': 'This is a test video transcription',
            'timestamp': '2023-04-01T12:00:00',
            'job_name': 'transcribe-test-uuid',
            'media_type': 'video'
        }
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_video.json', expected_dict)
        
        self.assertEqual(result, 'transcriptions/test_video.json')

    def test_transcription_result_model(self):
        # Test model creation and serialization
        result = TranscriptionResult(
            original_file='test.mp3',
            transcription_text='Hello world',
            timestamp='2023-04-01T12:00:00',
            job_name='test-job',
            media_type='audio'
        )
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict['original_file'], 'test.mp3')
        self.assertEqual(result_dict['transcription_text'], 'Hello world')
        self.assertEqual(result_dict['timestamp'], '2023-04-01T12:00:00')
        self.assertEqual(result_dict['job_name'], 'test-job')
        self.assertEqual(result_dict['media_type'], 'audio')
        
        # Test from_dict method
        new_result = TranscriptionResult.from_dict(result_dict)
        self.assertEqual(new_result.original_file, 'test.mp3')
        self.assertEqual(new_result.transcription_text, 'Hello world')
        self.assertEqual(new_result.timestamp, '2023-04-01T12:00:00')
        self.assertEqual(new_result.job_name, 'test-job')
        self.assertEqual(new_result.media_type, 'audio')
        
        # Test with video media type
        video_result = TranscriptionResult(
            original_file='test.mp4',
            transcription_text='Hello world',
            timestamp='2023-04-01T12:00:00',
            media_type='video'
        )
        self.assertEqual(video_result.media_type, 'video')
        
        # Test default media type (for backward compatibility)
        default_result = TranscriptionResult(
            original_file='test.mp3',
            transcription_text='Hello world',
            timestamp='2023-04-01T12:00:00'
        )
        self.assertEqual(default_result.media_type, 'audio')  # Should default to 'audio'

if __name__ == '__main__':
    unittest.main() 