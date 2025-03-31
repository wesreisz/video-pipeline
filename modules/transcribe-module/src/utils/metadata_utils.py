"""Utility functions for handling metadata sanitization."""
import re
from typing import Dict, Optional

def sanitize_metadata(metadata: Optional[Dict[str, str]]) -> Dict[str, str]:
    """
    Sanitize metadata by removing or replacing potentially problematic characters while preserving
    valid punctuation and formatting.
    
    Args:
        metadata (Optional[Dict[str, str]]): The metadata dictionary to sanitize
        
    Returns:
        Dict[str, str]: Sanitized metadata dictionary
        
    Example:
        >>> metadata = {
        ...     'title': 'My <script>alert("xss")</script> Talk!',
        ...     'track': 'AI/ML & Deep-Learning Track @2024'
        ... }
        >>> sanitize_metadata(metadata)
        {'title': 'My Talk!', 'track': 'AI/ML & Deep-Learning Track 2024'}
    """
    if not metadata:
        return {}
    
    sanitized = {}
    
    # Define patterns for sanitization in order of application
    patterns = [
        # Remove script tags and their content first
        (re.compile(r'<script\b[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL), ''),
        # Remove style tags and their content
        (re.compile(r'<style\b[^>]*>.*?</style>', re.IGNORECASE | re.DOTALL), ''),
        # Remove HTML comments
        (re.compile(r'<!--.*?-->', re.DOTALL), ''),
        # Remove HTML/XML tags
        (re.compile(r'<[^>]+>'), ' '),
        # Replace control characters and excessive whitespace with a single space
        (re.compile(r'[\x00-\x1F\x7F\s]+'), ' '),
        # First pass: Handle special cases
        (re.compile(r'(?<=\d):(?=\d{2}\b)'), 'TIMECOLON'),  # Preserve time colons
        (re.compile(r'(?<=[A-Za-z])/(?=[A-Za-z])'), 'SLASH'),  # Preserve category slashes
        (re.compile(r'&(?=\s|$)'), 'AMPERSAND'),  # Preserve standalone ampersands
        # Remove special characters except allowed punctuation
        (re.compile(r'[^\w\s\-.,!?()\'\"&/:@]+'), ' '),
        # Restore special cases
        (re.compile(r'TIMECOLON'), ':'),
        (re.compile(r'SLASH'), '/'),
        (re.compile(r'AMPERSAND'), '&'),
        # Clean up specific patterns
        (re.compile(r'(?<=\d)\s+(?=:)'), ''),  # Remove space before colon in time
        (re.compile(r'(?<=[AP])\s+(?=M\b)'), ''),  # Fix AM/PM spacing
        (re.compile(r'\s*&\s*'), ' & '),  # Normalize spaces around ampersands
        (re.compile(r'\s*/\s*'), '/'),  # Remove spaces around slashes
        # Replace multiple spaces with single space
        (re.compile(r'\s+'), ' ')
    ]
    
    # Allowed metadata keys
    allowed_keys = {'speaker', 'title', 'track', 'day'}
    
    for key, value in metadata.items():
        # Skip if key is not in allowed keys
        if key not in allowed_keys:
            continue
            
        if not isinstance(value, str):
            # Convert non-string values to strings
            value = str(value)
        
        # Apply sanitization patterns in order
        sanitized_value = value
        for pattern, replacement in patterns:
            sanitized_value = pattern.sub(replacement, sanitized_value)
        
        # Clean up extra whitespace
        sanitized_value = sanitized_value.strip()
        
        # Truncate if too long (e.g., 256 characters)
        if len(sanitized_value) > 256:
            sanitized_value = sanitized_value[:253] + '...'
            
        # Only add non-empty values
        if sanitized_value:
            sanitized[key] = sanitized_value
    
    return sanitized 