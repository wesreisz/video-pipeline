import json
import logging
import traceback

logger = logging.getLogger()

def handle_error(exception, message="An error occurred"):
    """
    Standardized error handler for Lambda functions
    
    Args:
        exception: The exception that was caught
        message: A human-readable message describing the error
        
    Returns:
        dict: Formatted error response for API Gateway
    """
    error_type = type(exception).__name__
    error_message = str(exception)
    stack_trace = traceback.format_exc()
    
    logger.error(
        f"{message}: {error_type} - {error_message}\n"
        f"Stack trace: {stack_trace}"
    )
    
    return {
        'statusCode': 500,
        'body': json.dumps({
            'error': error_type,
            'message': message,
            'details': error_message
        })
    } 