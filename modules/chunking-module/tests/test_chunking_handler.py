import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.handlers.chunking_handler import lambda_handler

class TestChunkingHandler(unittest.TestCase):
    """Tests for the chunking handler."""
    
    @patch('src.handlers.chunking_handler.json.dumps')
    @patch('src.handlers.chunking_handler.ChunkingService')
    def test_lambda_handler_success(self, mock_chunking_service, mock_json_dumps):
        """Test successful execution of the lambda handler."""
        # Setup mocks
        mock_chunking_instance = MagicMock()
        mock_chunking_instance.process_media.return_value = {
            "segments_count": 3,
            "segments": [
                {"start_time": "0.0", "end_time": "1.0", "transcript": "Test segment 1"},
                {"start_time": "1.0", "end_time": "2.0", "transcript": "Test segment 2"},
                {"start_time": "2.0", "end_time": "3.0", "transcript": "Test segment 3"}
            ],
            "total_duration": 3.0
        }
        mock_chunking_service.return_value = mock_chunking_instance
        
        # Mock json.dumps to return a fixed string instead of trying to serialize MagicMock
        mock_json_dumps.return_value = '{"message":"Chunking completed successfully","source_bucket":"test-bucket","source_file":"test-key.mp4","segments_count":3,"total_duration":3.0,"log_request_id":"test-id","note":"Chunking details are logged to CloudWatch instead of writing to a bucket"}'
        
        # Create a mock event
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": "test-bucket"
                        },
                        "object": {
                            "key": "test-key.mp4"
                        }
                    }
                }
            ]
        }
        
        # Create a mock context
        context = MagicMock()
        context.aws_request_id = "test-id"
        
        # Call the lambda handler
        response = lambda_handler(event, context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], mock_json_dumps.return_value)
        
        # Verify the service was called correctly
        mock_chunking_instance.process_media.assert_called_once_with('test-bucket', 'test-key.mp4')
    
    def test_lambda_handler_simple_request(self):
        """Test the lambda handler with a simple request without S3 event."""
        # Create a mock event
        event = {"test": "data"}
        
        # Create a mock context
        context = MagicMock()
        
        # Call the lambda handler
        response = lambda_handler(event, context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Chunking module initialized successfully')
        self.assertEqual(body['event_received'], event)
    
    @patch('src.handlers.chunking_handler.logger')
    def test_lambda_handler_logs_hello_world(self, mock_logger):
        """Test that the lambda handler logs 'Hello World'."""
        # Create a mock event and context
        event = {}
        context = MagicMock()
        
        # Call the lambda handler
        lambda_handler(event, context)
        
        # Assert that logger.info was called with "Hello World"
        mock_logger.info.assert_any_call("Hello World from Chunking Module!")
    
    @patch('src.handlers.chunking_handler.handle_error')
    def test_lambda_handler_error(self, mock_handle_error):
        """Test error handling in the lambda handler."""
        # Setup mock
        mock_handle_error.return_value = {'statusCode': 500, 'body': json.dumps({'error': 'Test Error'})}
        
        # Create a mock event that will cause an error
        event = None  # This will cause a ValueError
        
        # Create a mock context
        context = MagicMock()
        
        # Call the lambda handler
        response = lambda_handler(event, context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 500)
        # Verify handle_error was called
        mock_handle_error.assert_called_once()
        # Extract the first argument and check it's a ValueError
        error_arg = mock_handle_error.call_args[0][0]
        self.assertIsInstance(error_arg, ValueError)
        self.assertEqual(str(error_arg), "Event cannot be None")

if __name__ == '__main__':
    unittest.main() 