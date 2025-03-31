import pytest
from handlers.chunking_handler import generate_chunk_hash

def test_generate_chunk_hash_deterministic():
    """Test that the same inputs always produce the same hash."""
    original_file = "media/1 - Welcome.mp4"
    segment_id = 0
    
    # Generate hash twice with same inputs
    hash1 = generate_chunk_hash(original_file, segment_id)
    hash2 = generate_chunk_hash(original_file, segment_id)
    
    assert hash1 == hash2, "Hash should be deterministic for same inputs"

def test_generate_chunk_hash_different_inputs():
    """Test that different inputs produce different hashes."""
    original_file = "media/1 - Welcome.mp4"
    
    # Generate hashes for different segment IDs
    hash1 = generate_chunk_hash(original_file, 0)
    hash2 = generate_chunk_hash(original_file, 1)
    
    assert hash1 != hash2, "Different segment IDs should produce different hashes"
    
    # Generate hashes for different files
    hash3 = generate_chunk_hash("media/2 - Introduction.mp4", 0)
    assert hash1 != hash3, "Different files should produce different hashes"

def test_generate_chunk_hash_format():
    """Test that the hash has the expected format and length."""
    original_file = "media/1 - Welcome.mp4"
    segment_id = 0
    
    hash_value = generate_chunk_hash(original_file, segment_id)
    
    # Check that hash is a string
    assert isinstance(hash_value, str), "Hash should be a string"
    
    # Check hash length (should be exactly 10 characters)
    assert len(hash_value) == 10, "Hash should be exactly 10 characters"
    
    # Check that hash only contains valid characters (hexadecimal)
    assert all(c in '0123456789abcdef' for c in hash_value.lower()), "Hash should only contain hexadecimal characters"

def test_generate_chunk_hash_special_characters():
    """Test that the function handles special characters in filenames correctly."""
    original_files = [
        "media/file with spaces.mp4",
        "media/file_with_underscore.mp4",
        "media/file-with-dashes.mp4",
        "media/file.with.dots.mp4",
        "media/file@with@special#chars.mp4"
    ]
    
    for file in original_files:
        try:
            hash_value = generate_chunk_hash(file, 0)
            assert isinstance(hash_value, str), f"Failed to generate valid hash for {file}"
        except Exception as e:
            pytest.fail(f"Failed to handle special characters in filename: {file}, error: {str(e)}")

def test_generate_chunk_hash_invalid_inputs():
    """Test that the function handles invalid inputs appropriately."""
    with pytest.raises(ValueError):
        generate_chunk_hash("", 0)  # Empty filename
        
    with pytest.raises(ValueError):
        generate_chunk_hash(None, 0)  # None filename
        
    with pytest.raises(ValueError):
        generate_chunk_hash("media/file.mp4", None)  # None segment_id
        
    with pytest.raises(ValueError):
        generate_chunk_hash("media/file.mp4", -1)  # Negative segment_id 