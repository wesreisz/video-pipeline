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
        self.service.output_bucket = 'test-output-bucket'
    
    @patch('tempfile.NamedTemporaryFile')
    def test_process_audio(self, mock_temp_file):
        # Setup mocks
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test_audio.mp3'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        
        self.service.s3_utils.get_current_timestamp.return_value = '2023-04-01T12:00:00'
        self.service._transcribe_audio = MagicMock(return_value="This is a test transcription")
        
        # Call the method being tested
        result = self.service.process_audio('test-bucket', 'audio/test_audio.mp3')
        
        # Assertions
        self.service.s3_utils.download_file.assert_called_once_with(
            'test-bucket', 'audio/test_audio.mp3', '/tmp/test_audio.mp3')
        
        self.service._transcribe_audio.assert_called_once_with('/tmp/test_audio.mp3')
        
        expected_dict = {
            'original_file': 'audio/test_audio.mp3',
            'transcription_text': 'This is a test transcription',
            'timestamp': '2023-04-01T12:00:00'
        }
        
        self.service.s3_utils.upload_json.assert_called_once_with(
            'test-output-bucket', 'transcriptions/test_audio.json', expected_dict)
        
        self.assertEqual(result, 'transcriptions/test_audio.json')

    def test_transcription_result_model(self):
        # Test model creation and serialization
        result = TranscriptionResult(
            original_file='test.mp3',
            transcription_text='Hello world',
            timestamp='2023-04-01T12:00:00'
        )
        
        # Test to_dict method
        result_dict = result.to_dict()
        self.assertEqual(result_dict['original_file'], 'test.mp3')
        self.assertEqual(result_dict['transcription_text'], 'Hello world')
        self.assertEqual(result_dict['timestamp'], '2023-04-01T12:00:00')
        
        # Test from_dict method
        new_result = TranscriptionResult.from_dict(result_dict)
        self.assertEqual(new_result.original_file, 'test.mp3')
        self.assertEqual(new_result.transcription_text, 'Hello world')
        self.assertEqual(new_result.timestamp, '2023-04-01T12:00:00')

if __name__ == '__main__':
    unittest.main() 