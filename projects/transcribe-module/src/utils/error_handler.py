import json
import logging
import traceback

logger = logging.getLogger()

def handle_error(exception, message="An error occurred"):
    """
    Handle exceptions and return appropriate Lambda response
    
    Args:
        exception: The caught exception
        message: A descriptive error message
        
    Returns:
        dict: Response containing error details
    """
    error_trace = traceback.format_exc()
    logger.error(f"{message}: {str(exception)}")
    logger.error(error_trace)
    
    return {
        'statusCode': 500,
        'body': json.dumps({
            'error': str(exception),
            'message': message
        })
    } 