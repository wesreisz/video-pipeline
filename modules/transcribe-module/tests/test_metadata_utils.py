"""Tests for metadata sanitization utilities."""
import pytest
from src.utils.metadata_utils import sanitize_metadata

def test_sanitize_metadata_with_valid_input():
    """Test sanitization with valid metadata."""
    metadata = {
        'speaker': 'John Doe',
        'title': 'My Talk About Python!',
        'track': 'Technical Track',
        'day': 'Monday'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == metadata

def test_sanitize_metadata_with_html_injection():
    """Test sanitization removes HTML tags and script content."""
    metadata = {
        'speaker': '<script>alert("xss")</script>John Doe',
        'title': '<b>My Talk</b>',
        'track': 'Technical <span>Track</span>',
        'day': '<b>Monday</b>'
    }
    expected = {
        'speaker': 'John Doe',
        'title': 'My Talk',
        'track': 'Technical Track',
        'day': 'Monday'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_with_special_chars():
    """Test sanitization handles special characters."""
    metadata = {
        'speaker': 'John.Doe@company.com',  # Email address
        'title': '$Special$ Talk #2024',  # Currency and hashtag
        'track': 'AI/ML & Cloud/DevOps',  # Technical track with slashes
        'day': 'Monday @ 9:00 AM'  # Time with @ symbol
    }
    expected = {
        'speaker': 'John.Doe@company.com',
        'title': 'Special Talk 2024',
        'track': 'AI/ML & Cloud/DevOps',
        'day': 'Monday @ 9:00 AM'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_with_invalid_special_chars():
    """Test sanitization removes invalid special characters."""
    metadata = {
        'speaker': 'John#$%^Doe',
        'title': '***Important!!!***',
        'track': '|Technical~Track|',
        'day': '>>Monday<<'
    }
    expected = {
        'speaker': 'John Doe',
        'title': 'Important!!!',
        'track': 'Technical Track',
        'day': 'Monday'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_with_control_chars():
    """Test sanitization removes control characters."""
    metadata = {
        'speaker': 'John\x00Doe\x1F',
        'title': 'My\nTalk\r\n',
        'track': 'Tech\tTrack',
        'day': 'Monday\b'  # Backspace at end
    }
    expected = {
        'speaker': 'John Doe',
        'title': 'My Talk',
        'track': 'Tech Track',
        'day': 'Monday'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_with_long_values():
    """Test sanitization truncates long values."""
    long_string = 'a' * 300
    metadata = {
        'speaker': long_string,
        'title': long_string,
        'track': long_string,
        'day': long_string
    }
    for value in sanitize_metadata(metadata).values():
        assert len(value) <= 256
        assert value.endswith('...')

def test_sanitize_metadata_with_invalid_keys():
    """Test sanitization removes invalid keys."""
    metadata = {
        'speaker': 'John Doe',
        'title': 'My Talk',
        'invalid_key': 'Should be removed',
        'another_invalid': 'Also removed'
    }
    sanitized = sanitize_metadata(metadata)
    assert 'invalid_key' not in sanitized
    assert 'another_invalid' not in sanitized
    assert sanitized == {
        'speaker': 'John Doe',
        'title': 'My Talk'
    }

def test_sanitize_metadata_with_none():
    """Test sanitization handles None input."""
    assert sanitize_metadata(None) == {}

def test_sanitize_metadata_with_empty_dict():
    """Test sanitization handles empty dict."""
    assert sanitize_metadata({}) == {}

def test_sanitize_metadata_with_non_string_values():
    """Test sanitization converts non-string values to strings."""
    metadata = {
        'speaker': 123,
        'title': True,
        'track': ['Technical', 'Track'],
        'day': {'key': 'value'}
    }
    sanitized = sanitize_metadata(metadata)
    assert all(isinstance(v, str) for v in sanitized.values())

def test_sanitize_metadata_real_world_scenario():
    """
    Test sanitization with a real-world scenario including complex metadata
    that might come from various sources like conference systems.
    """
    # Complex metadata that might come from a conference system
    metadata = {
        'speaker': 'Dr. Jane Smith, Ph.D. <script>alert("xss")</script> & Associates',
        'title': '''Multi-line Title with "quotes"
                   and \x00control\x01characters
                   and <b>HTML</b>''',
        'track': 'AI/ML & Deep-Learning Track @2024',
        'day': 'Monday (Morning) - 9:00 AM',
        # Invalid fields that should be removed
        'session_id': '12345',
        'room_number': 'A-101',
        'special_notes': 'VIP Speaker!!!',
        'html_description': '<p>Some description</p>'
    }

    expected = {
        'speaker': 'Dr. Jane Smith, Ph.D. & Associates',
        'title': 'Multi-line Title with "quotes" and control characters and HTML',
        'track': 'AI/ML & Deep-Learning Track @2024',
        'day': 'Monday (Morning) - 9:00 AM'
    }

    sanitized = sanitize_metadata(metadata)

    # Test exact matches
    assert sanitized == expected

    # Test that all invalid keys were removed
    invalid_keys = {'session_id', 'room_number', 'special_notes', 'html_description'}
    assert all(key not in sanitized for key in invalid_keys)

    # Test that no HTML remains
    assert all('<' not in value and '>' not in value for value in sanitized.values())

    # Test that no control characters remain
    assert all(not any(ord(c) < 32 for c in value) for value in sanitized.values())

    # Test that values are properly formatted
    assert all(value == value.strip() for value in sanitized.values())
    assert all(not value.endswith('...') for value in sanitized.values())  # No truncation needed
    assert all(len(value) <= 256 for value in sanitized.values())

@pytest.mark.parametrize("invalid_input", [
    {'speaker': None},
    {'title': float('inf')},
    {'track': Exception('test')},
    {'day': object()},
])
def test_sanitize_metadata_with_exotic_types(invalid_input):
    """Test sanitization handles exotic Python types without breaking."""
    sanitized = sanitize_metadata(invalid_input)
    assert isinstance(sanitized, dict)
    # Should either convert to string or exclude the value
    for value in sanitized.values():
        assert isinstance(value, str)
        assert len(value) <= 256

def test_sanitize_metadata_with_complex_html():
    """Test sanitization with more complex HTML scenarios."""
    metadata = {
        'speaker': '<div class="name">John <script>alert(1)</script>Doe</div>',
        'title': '<style>.bad{}</style>My Talk<!-- comment -->',
        'track': '<a href="javascript:alert(1)">Technical Track</a>',
        'day': '<iframe src="evil.com"></iframe>Monday'
    }
    expected = {
        'speaker': 'John Doe',
        'title': 'My Talk',
        'track': 'Technical Track',
        'day': 'Monday'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_edge_cases():
    """Test sanitization with edge cases and special characters."""
    metadata = {
        'speaker': '  John & Doe  ',  # Extra spaces and ampersand
        'title': 'My Talk!!! (2024)',  # Multiple punctuation and parentheses
        'track': 'Technical-Track.1',  # Hyphen and period
        'day': 'Mon.'  # Abbreviated with period
    }
    expected = {
        'speaker': 'John & Doe',
        'title': 'My Talk!!! (2024)',
        'track': 'Technical-Track.1',
        'day': 'Mon.'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_preserves_words():
    """Test sanitization preserves word boundaries."""
    metadata = {
        'speaker': '  John   Doe  ',  # Multiple spaces
        'title': 'My\n\r\nTalk',  # Multiple newlines
        'track': 'Tech\t \tTrack',  # Multiple tabs and spaces
        'day': 'Monday'
    }
    expected = {
        'speaker': 'John Doe',
        'title': 'My Talk',
        'track': 'Tech Track',
        'day': 'Monday'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected

def test_sanitize_metadata_with_edge_cases():
    """Test sanitization with edge cases that should be preserved."""
    metadata = {
        'speaker': 'Dr. J. Smith & Dr. M. Jones',  # Multiple names with initials
        'title': '"Advanced AI/ML" (2024)',  # Quotes and parentheses
        'track': 'Cloud/DevOps & AI/ML',  # Multiple slashes
        'day': 'Monday @ 9:00 AM - Track A'  # Time with @ symbol
    }
    expected = {
        'speaker': 'Dr. J. Smith & Dr. M. Jones',
        'title': '"Advanced AI/ML" (2024)',
        'track': 'Cloud/DevOps & AI/ML',
        'day': 'Monday @ 9:00 AM - Track A'
    }
    sanitized = sanitize_metadata(metadata)
    assert sanitized == expected 