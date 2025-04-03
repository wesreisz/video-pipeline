import sys
from loguru import logger
import os

def setup_logger():
    """
    Configure the logger for the question module.
    """
    # Remove default handler
    logger.remove()
    
    # Get log level from environment variable or default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Add handler with custom format
    logger.add(
        sys.stderr,
        format="{time} | {level} | {message}",
        level=log_level
    )
    
    return logger 