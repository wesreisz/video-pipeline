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
    
    @patch('time.sleep', return_value=None)
    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_audio(self, mock_uuid, mock_sleep):
        """Test processing an audio file"""
        # Setup mocks
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._wait_for_transcription = MagicMock(return_value=("This is a test transcription", [
            {"type": "pronunciation", "start_time": "0.0", "end_time": "0.62", "content": "This"},
            {"type": "pronunciation", "start_time": "0.62", "end_time": "0.81", "content": "is"},
            {"type": "pronunciation", "start_time": "0.81", "end_time": "0.93", "content": "a"},
            {"type": "pronunciation", "start_time": "0.93", "end_time": "1.25", "content": "test"},
            {"type": "pronunciation", "start_time": "1.25", "end_time": "2.21", "content": "transcription"}
        ]))
        
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
            'media_type': 'audio',
            'segments': [
                {"type": "pronunciation", "start_time": "0.0", "end_time": "0.62", "content": "This"},
                {"type": "pronunciation", "start_time": "0.62", "end_time": "0.81", "content": "is"},
                {"type": "pronunciation", "start_time": "0.81", "end_time": "0.93", "content": "a"},
                {"type": "pronunciation", "start_time": "0.93", "end_time": "1.25", "content": "test"},
                {"type": "pronunciation", "start_time": "1.25", "end_time": "2.21", "content": "transcription"}
            ]
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
        self.service._wait_for_transcription = MagicMock(return_value=("This is a test video transcription", [
            {"type": "pronunciation", "start_time": "0.0", "end_time": "0.62", "content": "This"},
            {"type": "pronunciation", "start_time": "0.62", "end_time": "0.81", "content": "is"},
            {"type": "pronunciation", "start_time": "0.81", "end_time": "0.93", "content": "a"},
            {"type": "pronunciation", "start_time": "0.93", "end_time": "1.25", "content": "test"},
            {"type": "pronunciation", "start_time": "1.25", "end_time": "1.71", "content": "video"},
            {"type": "pronunciation", "start_time": "1.71", "end_time": "2.51", "content": "transcription"}
        ]))
        
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
            'media_type': 'video',
            'segments': [
                {"type": "pronunciation", "start_time": "0.0", "end_time": "0.62", "content": "This"},
                {"type": "pronunciation", "start_time": "0.62", "end_time": "0.81", "content": "is"},
                {"type": "pronunciation", "start_time": "0.81", "end_time": "0.93", "content": "a"},
                {"type": "pronunciation", "start_time": "0.93", "end_time": "1.25", "content": "test"},
                {"type": "pronunciation", "start_time": "1.25", "end_time": "1.71", "content": "video"},
                {"type": "pronunciation", "start_time": "1.71", "end_time": "2.51", "content": "transcription"}
            ]
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