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
        ], [
            {"id": 0, "transcript": "This is a test transcription.", "start_time": "0.0", "end_time": "2.21", "items": [0, 1, 2, 3, 4]}
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
            ],
            'audio_segments': [
                {"id": 0, "transcript": "This is a test transcription.", "start_time": "0.0", "end_time": "2.21", "items": [0, 1, 2, 3, 4]}
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
        ], [
            {"id": 0, "transcript": "This is a test video transcription.", "start_time": "0.0", "end_time": "2.51", "items": [0, 1, 2, 3, 4, 5]}
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
            ],
            'audio_segments': [
                {"id": 0, "transcript": "This is a test video transcription.", "start_time": "0.0", "end_time": "2.51", "items": [0, 1, 2, 3, 4, 5]}
            ]
        }
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_video.json', expected_dict)
        
        self.assertEqual(result, 'transcriptions/test_video.json')

    @patch('time.sleep', return_value=None)
    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_wav_file(self, mock_uuid, mock_sleep):
        """Test processing a WAV audio file to verify format normalization"""
        # Setup mocks
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._wait_for_transcription = MagicMock(return_value=("This is a test WAV transcription", [
            {"type": "pronunciation", "start_time": "0.0", "end_time": "1.0", "content": "Test"}
        ], [
            {"id": 0, "transcript": "This is a test WAV transcription.", "start_time": "0.0", "end_time": "1.0", "items": [0]}
        ]))
        
        # Call the method being tested
        result = self.service.process_media('test-bucket', 'audio/test_audio.wav')
        
        # Assertions
        self.service.transcribe_client.start_transcription_job.assert_called_once()
        
        # Check that the correct arguments were passed
        call_args = self.service.transcribe_client.start_transcription_job.call_args[1]
        self.assertEqual(call_args['MediaFormat'], 'wav')  # Should normalize to wav
        self.assertEqual(call_args['Media']['MediaFileUri'], 's3://test-bucket/audio/test_audio.wav')
        
        # Check media_type in result
        expected_dict = {
            'original_file': 'audio/test_audio.wav',
            'transcription_text': 'This is a test WAV transcription',
            'timestamp': '2023-04-01T12:00:00',
            'job_name': 'transcribe-test-uuid',
            'media_type': 'audio',
            'segments': [
                {"type": "pronunciation", "start_time": "0.0", "end_time": "1.0", "content": "Test"}
            ],
            'audio_segments': [
                {"id": 0, "transcript": "This is a test WAV transcription.", "start_time": "0.0", "end_time": "1.0", "items": [0]}
            ]
        }
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_audio.json', expected_dict)

    @patch('time.sleep', return_value=None)
    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_webm_file(self, mock_uuid, mock_sleep):
        """Test processing a WEBM video file"""
        # Setup mocks
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._wait_for_transcription = MagicMock(return_value=("This is a test WEBM transcription", [
            {"type": "pronunciation", "start_time": "0.0", "end_time": "1.0", "content": "Test"}
        ], [
            {"id": 0, "transcript": "This is a test WEBM transcription.", "start_time": "0.0", "end_time": "1.0", "items": [0]}
        ]))
        
        # Call the method being tested
        result = self.service.process_media('test-bucket', 'videos/test_video.webm')
        
        # Assertions
        self.service.transcribe_client.start_transcription_job.assert_called_once()
        
        # Check that the correct arguments were passed
        call_args = self.service.transcribe_client.start_transcription_job.call_args[1]
        self.assertEqual(call_args['MediaFormat'], 'webm')
        self.assertEqual(call_args['Media']['MediaFileUri'], 's3://test-bucket/videos/test_video.webm')
        
        # Verify that webm is recognized as video
        expected_dict = {
            'original_file': 'videos/test_video.webm',
            'transcription_text': 'This is a test WEBM transcription',
            'timestamp': '2023-04-01T12:00:00',
            'job_name': 'transcribe-test-uuid',
            'media_type': 'video',  # Should be video for webm files
            'segments': [
                {"type": "pronunciation", "start_time": "0.0", "end_time": "1.0", "content": "Test"}
            ],
            'audio_segments': [
                {"id": 0, "transcript": "This is a test WEBM transcription.", "start_time": "0.0", "end_time": "1.0", "items": [0]}
            ]
        }
        
        # Get the actual dictionary passed to upload_json
        actual_dict = self.service.s3_utils.upload_json.call_args[0][2]
        
        # Ensure media_type is correct before assertion
        self.assertEqual(actual_dict['media_type'], 'video')
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_video.json', expected_dict)
            
        self.assertEqual(result, 'transcriptions/test_video.json')

    @patch('time.sleep', return_value=None)
    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_unknown_extension(self, mock_uuid, mock_sleep):
        """Test processing a file with unknown extension"""
        # Setup mocks
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._wait_for_transcription = MagicMock(return_value=("This is a test unknown extension transcription", [
            {"type": "pronunciation", "start_time": "0.0", "end_time": "1.0", "content": "Test"}
        ], [
            {"id": 0, "transcript": "This is a test unknown extension transcription.", "start_time": "0.0", "end_time": "1.0", "items": [0]}
        ]))
        
        # Call the method being tested
        result = self.service.process_media('test-bucket', 'audio/test_audio.xyz')
        
        # Assertions
        self.service.transcribe_client.start_transcription_job.assert_called_once()
        
        # Check that it defaults to correct format/type
        call_args = self.service.transcribe_client.start_transcription_job.call_args[1]
        self.assertEqual(call_args['MediaFormat'], 'xyz')  # Should use extension
        self.assertEqual(call_args['Media']['MediaFileUri'], 's3://test-bucket/audio/test_audio.xyz')
        
        # It should default to audio type for unknown extensions
        expected_dict = {
            'original_file': 'audio/test_audio.xyz',
            'transcription_text': 'This is a test unknown extension transcription',
            'timestamp': '2023-04-01T12:00:00',
            'job_name': 'transcribe-test-uuid',
            'media_type': 'audio',
            'segments': [
                {"type": "pronunciation", "start_time": "0.0", "end_time": "1.0", "content": "Test"}
            ],
            'audio_segments': [
                {"id": 0, "transcript": "This is a test unknown extension transcription.", "start_time": "0.0", "end_time": "1.0", "items": [0]}
            ]
        }
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_audio.json', expected_dict)

    @patch('uuid.uuid4', return_value='test-uuid')
    def test_process_media_transcribe_client_exception(self, mock_uuid):
        """Test exception handling when the transcribe client raises an exception"""
        # Setup mock to raise exception
        self.service.transcribe_client.start_transcription_job.side_effect = Exception("AWS Transcribe error")
        
        # Call the method and check for exception
        with self.assertRaises(Exception) as context:
            self.service.process_media('test-bucket', 'audio/test_audio.mp3')
            
        # Verify the exception is propagated
        self.assertTrue("AWS Transcribe error" in str(context.exception))

    @patch('time.sleep', return_value=None)
    def test_wait_for_transcription_completed(self, mock_sleep):
        """Test the _wait_for_transcription method when job completes successfully"""
        # Mock successful response
        self.service.transcribe_client.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }
        
        # Mock S3 download of the transcript JSON
        transcript_json = {
            'results': {
                'transcripts': [{'transcript': 'This is a test transcription'}],
                'items': [
                    {
                        'type': 'pronunciation',
                        'start_time': '0.0',
                        'end_time': '0.5',
                        'alternatives': [{'content': 'This', 'confidence': '0.95'}]
                    },
                    {
                        'type': 'punctuation',
                        'alternatives': [{'content': '.', 'confidence': '0.99'}]
                    }
                ],
                'audio_segments': [
                    {
                        'id': 0,
                        'transcript': 'This is a test transcription.',
                        'start_time': '0.0',
                        'end_time': '0.5',
                        'items': [0, 1]
                    }
                ]
            }
        }
        self.service.s3_utils.download_json.return_value = transcript_json
        
        # Call the method
        transcription_text, segments, audio_segments = self.service._wait_for_transcription('test-job')
        
        # Assertions
        self.assertEqual(transcription_text, 'This is a test transcription')
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]['content'], 'This')
        self.assertEqual(segments[0]['confidence'], '0.95')
        self.assertEqual(segments[1]['content'], '.')
        
        # Test audio segments
        self.assertEqual(len(audio_segments), 1)
        self.assertEqual(audio_segments[0]['transcript'], 'This is a test transcription.')
        self.assertEqual(audio_segments[0]['start_time'], '0.0')
        self.assertEqual(audio_segments[0]['end_time'], '0.5')
        self.assertEqual(audio_segments[0]['items'], [0, 1])

    @patch('time.sleep', return_value=None)
    def test_wait_for_transcription_failed(self, mock_sleep):
        """Test the _wait_for_transcription method when job fails"""
        # Mock failure response
        self.service.transcribe_client.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'FAILED',
                'FailureReason': 'Invalid media format'
            }
        }
        
        # Call the method and check for exception
        with self.assertRaises(Exception) as context:
            self.service._wait_for_transcription('test-job')
            
        # Verify the correct exception message
        self.assertEqual(str(context.exception), 'Transcription job failed: Invalid media format')

    @patch('time.sleep', return_value=None)
    def test_wait_for_transcription_timeout(self, mock_sleep):
        """Test the _wait_for_transcription method when job times out"""
        # Mock in-progress response
        self.service.transcribe_client.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'IN_PROGRESS'
            }
        }
        
        # Call the method with low max_attempts to trigger timeout quickly
        with self.assertRaises(Exception) as context:
            self.service._wait_for_transcription('test-job', max_attempts=2, delay_seconds=0)
            
        # Verify the timeout exception message
        self.assertEqual(
            str(context.exception), 
            'Transcription job timed out after 2 attempts'
        )

    @patch('time.sleep', return_value=None)
    def test_wait_for_transcription_no_segments(self, mock_sleep):
        """Test handling when transcript has no segments"""
        # Setup mock
        self.service.transcribe_client.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED'
            }
        }
        
        # Create transcript json with no segments
        transcript_json = {
            'results': {
                'transcripts': [{'transcript': 'This is a test transcript'}],
                'items': []
            }
        }
        self.service.s3_utils.download_json.return_value = transcript_json
        
        # Call the method
        transcription_text, segments, audio_segments = self.service._wait_for_transcription('test-job')
        
        # Assertions
        self.assertEqual(transcription_text, 'This is a test transcript')
        self.assertEqual(segments, [])
        self.assertEqual(audio_segments, [])

    @patch('os.environ.get')
    def test_service_initialization_with_custom_environment(self, mock_env_get):
        """Test service initialization with custom environment variables"""
        # Setup mock environment
        mock_env_get.side_effect = lambda key, default=None: {
            'TRANSCRIPTION_OUTPUT_BUCKET': 'custom-output-bucket',
            'TRANSCRIBE_REGION': 'eu-west-1'
        }.get(key, default)
        
        # Mock boto3 client creation
        with patch('boto3.client') as mock_boto3_client:
            # Create service
            service = TranscriptionService()
            
            # Assertions
            self.assertEqual(service.output_bucket, 'custom-output-bucket')
            self.assertEqual(service.region, 'eu-west-1')
            mock_boto3_client.assert_called_with('transcribe', region_name='eu-west-1')

    @patch('os.environ.get')
    def test_service_initialization_with_default_region(self, mock_env_get):
        """Test service initialization with default region"""
        # Setup mock environment - only set output bucket, not region
        mock_env_get.side_effect = lambda key, default=None: {
            'TRANSCRIPTION_OUTPUT_BUCKET': 'test-output-bucket'
        }.get(key, default)
        
        # Mock boto3 client creation
        with patch('boto3.client') as mock_boto3_client:
            # Create service
            service = TranscriptionService()
            
            # Assertions
            self.assertEqual(service.region, 'us-east-1')  # Should use default
            mock_boto3_client.assert_called_with('transcribe', region_name='us-east-1')

    def test_transcription_result_model(self):
        # Test model creation and serialization
        result = TranscriptionResult(
            original_file='test.mp3',
            transcription_text='Hello world',
            timestamp='2023-04-01T12:00:00',
            job_name='test-job',
            media_type='audio',
            segments=[{"type": "pronunciation", "content": "Hello"}],
            audio_segments=[{"id": 0, "transcript": "Hello world", "start_time": "0.0", "end_time": "1.0"}]
        )
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict['original_file'], 'test.mp3')
        self.assertEqual(result_dict['transcription_text'], 'Hello world')
        self.assertEqual(result_dict['timestamp'], '2023-04-01T12:00:00')
        self.assertEqual(result_dict['job_name'], 'test-job')
        self.assertEqual(result_dict['media_type'], 'audio')
        self.assertEqual(len(result_dict['segments']), 1)
        self.assertEqual(result_dict['segments'][0]['content'], 'Hello')
        self.assertEqual(len(result_dict['audio_segments']), 1)
        self.assertEqual(result_dict['audio_segments'][0]['transcript'], 'Hello world')
        
        # Test from_dict method
        new_result = TranscriptionResult.from_dict(result_dict)
        self.assertEqual(new_result.original_file, 'test.mp3')
        self.assertEqual(new_result.transcription_text, 'Hello world')
        self.assertEqual(new_result.timestamp, '2023-04-01T12:00:00')
        self.assertEqual(new_result.job_name, 'test-job')
        self.assertEqual(new_result.media_type, 'audio')
        self.assertEqual(len(new_result.segments), 1)
        self.assertEqual(new_result.segments[0]['content'], 'Hello')
        self.assertEqual(len(new_result.audio_segments), 1)
        self.assertEqual(new_result.audio_segments[0]['transcript'], 'Hello world')
        
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
        
        # Test with empty audio_segments (for backward compatibility)
        back_compat_result = TranscriptionResult.from_dict({
            'original_file': 'test.mp3',
            'transcription_text': 'Hello world',
            'timestamp': '2023-04-01T12:00:00'
        })
        self.assertEqual(back_compat_result.audio_segments, [])

if __name__ == '__main__':
    unittest.main() 