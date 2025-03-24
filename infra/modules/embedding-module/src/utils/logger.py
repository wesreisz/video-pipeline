import logging
import os
from typing import Optional

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting and log level.
    
    Args:
        name: Optional name for the logger (defaults to root logger if None)
        
    Returns:
        Configured logger instance
    """
    # Get logger instance
    logger = logging.getLogger(name)
    
    # Only add handler if it doesn't already have one
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    # Set log level from environment variable or default to INFO
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    return logger 