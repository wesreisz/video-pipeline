from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import json
from loguru import logger
import re
from utils.secrets import get_secrets_service
from utils.auth_util import AuthUtil
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

# Custom exceptions for better error handling
class QuestionProcessingError(Exception):
    """Base exception for question processing errors"""
    pass

class ValidationError(QuestionProcessingError):
    """Raised when request validation fails"""
    pass

class AuthorizationError(QuestionProcessingError):
    """Raised when authorization fails"""
    pass

class ConfigurationError(QuestionProcessingError):
    """Raised when there are issues with configuration or secrets"""
    pass

# Type definitions for better clarity
JsonResponse = Dict[str, Any]
Headers = Dict[str, str]

@dataclass
class QuestionRequest:
    """Data class representing a validated question request."""
    question: str
    email: str
    
    def validate(self) -> None:
        """
        Validates the request data. Raises ValidationError if invalid.
        """
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValidationError("Question must be a non-empty string about the transcripts")
        if not isinstance(self.email, str) or not validate_email(self.email):
            raise ValidationError("Invalid email format")

# Initialize services during cold start
_secrets_service = get_secrets_service()
_auth_util = AuthUtil()

# ----------------------------------------
# Validation Functions
# ----------------------------------------

def validate_email(email: str) -> bool:
    """
    Validate email format using regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_api_key_or_raise(headers: Dict[str, str]) -> None:
    """
    Validate the API key from request headers.
    Raises AuthorizationError if invalid.
    """
    api_key = headers.get('x-api-key')
    expected_key = _secrets_service.get_api_key()
    
    if not api_key or not expected_key:
        raise AuthorizationError("Missing API key")
        
    if api_key != expected_key:
        raise AuthorizationError("Invalid API key")

def parse_and_validate_request(event: Dict[str, Any]) -> QuestionRequest:
    """
    Parse and validate the request body from the Lambda event.
    Returns a validated QuestionRequest object.
    """
    if 'body' not in event:
        raise ValidationError("Missing request body")
        
    try:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in request body: {str(e)}")
    
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a JSON object")
    
    # Extract required fields
    question = body.get('question')
    email = body.get('email')
    
    if not question or not email:
        raise ValidationError("Missing required fields: question and email")
    
    # Create and validate request object
    request = QuestionRequest(question=question, email=email)
    request.validate()
    
    # Check authorization
    if not _auth_util.is_authorized(email):
        raise AuthorizationError(f"Email not authorized: {email}")
    
    return request

def setup_ai_services() -> Tuple[OpenAI, Pinecone]:
    """
    Initialize OpenAI and Pinecone services with API keys.
    """
    openai_api_key = _secrets_service.get_secret('openai_api_key')
    pinecone_api_key = _secrets_service.get_secret('pinecone_api_key')
    
    if not openai_api_key or not pinecone_api_key:
        raise ConfigurationError("Failed to retrieve required API keys")
    
    return OpenAI(api_key=openai_api_key), Pinecone(api_key=pinecone_api_key)

def process_question(request: QuestionRequest) -> Dict[str, Any]:
    """
    Process the question request using OpenAI and Pinecone services.
    Returns the processing result.
    """
    logger.info(f"Processing question from {request.email}")
    
    try:
        # Initialize AI services
        openai_client, pinecone_client = setup_ai_services()
        
        # Generate embedding
        embedding_response = openai_client.embeddings.create(
            input=request.question,
            model="text-embedding-ada-002"
        )
        query_embedding = embedding_response.data[0].embedding
        logger.info(f"Generated embedding of length: {len(query_embedding)}")
        
        # Query Pinecone
        index = pinecone_client.Index("talk-embeddings")
        pc_response = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True
        )
        
        # Extract metadata from matches
        metadata_list = [match['metadata'] for match in pc_response['matches']]
        return {'pinecone_matches': metadata_list}
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise QuestionProcessingError(f"Failed to process question: {str(e)}")

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized API response.
    """
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for processing question requests.
    Implements a clean request processing pipeline with proper error handling.
    """
    logger.info("Processing question event")
    
    try:
        # Step 1: Validate API key
        validate_api_key_or_raise(event.get('headers', {}))
        
        # Step 2: Parse and validate request
        request = parse_and_validate_request(event)
        
        # Step 3: Process the question
        result = process_question(request)
        
        # Step 4: Return success response
        return create_response(200, result)
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return create_response(400, {'error': str(e)})
        
    except AuthorizationError as e:
        logger.error(f"Authorization error: {str(e)}")
        return create_response(401, {'error': str(e)})
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})
        
    except QuestionProcessingError as e:
        logger.error(f"Processing error: {str(e)}")
        return create_response(500, {'error': 'Error processing request'})
        
    except Exception as e:
        logger.exception("Unexpected error")
        return create_response(500, {'error': 'Internal server error'}) 