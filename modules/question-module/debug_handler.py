#!/usr/bin/env python3
"""
Debug script for the question handler to identify the cause of 500 errors.
This helps us test the handler locally without deploying to AWS.
"""

import json
import sys
import os

# Add the src directory to Python path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_handler_imports():
    """Test if we can import all necessary modules."""
    print("🔍 Testing imports...")
    
    try:
        from handlers.question_handler import lambda_handler
        print("✅ Successfully imported lambda_handler")
        return True
    except ImportError as e:
        print(f"❌ Failed to import lambda_handler: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing lambda_handler: {e}")
        return False

def test_handler_with_mock_event():
    """Test the handler with a mock event."""
    print("\n🧪 Testing handler with mock event...")
    
    try:
        from handlers.question_handler import lambda_handler
        
        # Mock event that matches the API Gateway format
        mock_event = {
            'body': json.dumps({
                'question': 'What is the main topic discussed?',
                'email': 'test@example.com'
            }),
            'headers': {
                'x-api-key': 'test-api-key',
                'Content-Type': 'application/json'
            },
            'httpMethod': 'POST',
            'path': '/query'
        }
        
        # Mock context
        class MockContext:
            def __init__(self):
                self.function_name = 'test-function'
                self.function_version = '1'
                self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
                self.memory_limit_in_mb = 512
                self.remaining_time_in_millis = lambda: 30000

        print("📤 Sending mock event to handler...")
        print(f"Request body: {mock_event['body']}")
        print(f"Headers: {mock_event['headers']}")
        
        # Call the handler
        response = lambda_handler(mock_event, MockContext())
        
        print(f"\n📨 Response received:")
        print(f"Status Code: {response.get('statusCode')}")
        print(f"Response Body: {response.get('body')}")
        
        if response.get('statusCode') == 500:
            print("❌ Handler returned 500 error")
            return False
        else:
            print("✅ Handler executed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error testing handler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_setup():
    """Test if environment is properly configured."""
    print("\n🌍 Testing environment setup...")
    
    # Check Python path
    print(f"Python path: {sys.path}")
    
    # Check if we can import basic modules
    try:
        import boto3
        print("✅ boto3 available")
    except ImportError:
        print("❌ boto3 not available")
    
    try:
        import openai
        print("✅ openai available")
    except ImportError:
        print("❌ openai not available")
    
    try:
        import pinecone
        print("✅ pinecone available")
    except ImportError:
        print("❌ pinecone not available")
    
    try:
        from loguru import logger
        print("✅ loguru available")
    except ImportError:
        print("❌ loguru not available")

def main():
    """Main debug function."""
    print("🚀 Starting Question Handler Debug Session")
    print("=" * 50)
    
    # Test 1: Environment setup
    test_environment_setup()
    
    # Test 2: Import testing
    if not test_handler_imports():
        print("\n❌ Cannot proceed - import issues detected")
        return False
    
    # Test 3: Handler testing
    if not test_handler_with_mock_event():
        print("\n❌ Handler test failed")
        return False
    
    print("\n✅ All debug tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 