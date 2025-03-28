import logging
import os
from typing import Optional
from services.secrets_service import SecretsService

_secrets_service = None

def get_secrets_service():
    """Get or create a singleton SecretsService instance."""
    global _secrets_service
    if _secrets_service is None:
        _secrets_service = SecretsService()
    return _secrets_service

def get_logger(name: Optional[str] = None) -> logging.Logger:
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
    
    # Set log level from secrets or default to INFO
    secrets_service = get_secrets_service()
    log_level = (secrets_service.get_secret('log_level') or 'INFO').upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    return logger 