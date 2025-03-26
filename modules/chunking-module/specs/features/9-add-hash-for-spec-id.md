# Feature: Generate Deterministic Hash-based Chunk IDs

## Background
When processing audio/video segments in our pipeline, we need a way to uniquely and deterministically identify each chunk. Currently, we're using sequential numeric IDs, but we need a more robust solution that combines the original file name with the segment ID to create a unique identifier.

## Objective
Create a function that generates a deterministic hash from a combination of the original file name and segment ID. This hash will serve as a unique identifier for each chunk in our processing pipeline.

## Technical Requirements

### 1. Hash Generation Function
Create a function with the following signature:
```python
def generate_chunk_hash(original_file: str, segment_id: int) -> str:
    """
    Generate a deterministic hash from original file name and segment ID.
    Returns only the first 10 characters of the hash for brevity.
    
    Args:
        original_file: Path to the original media file
        segment_id: ID of the segment within the file
        
    Returns:
        A 10-character hexadecimal hash string
        
    Raises:
        ValueError: If inputs are invalid (None, empty string, or negative segment_id)
    """
```

### 2. Function Requirements
- Use SHA-256 for hash generation, but only return the first 10 characters
- Combine `original_file` and `segment_id` in a deterministic way (e.g., `f"{original_file}:{segment_id}"`)
- Return a 10-character hexadecimal string representation of the hash
- Handle special characters in filenames correctly
- Validate inputs and raise appropriate errors

### 3. Test Cases
Create unit tests that verify:

1. **Deterministic Behavior**
```python
def test_generate_chunk_hash_deterministic():
    """Test that the same inputs always produce the same hash."""
    original_file = "media/1 - Welcome.mp4"
    segment_id = 0
    
    hash1 = generate_chunk_hash(original_file, segment_id)
    hash2 = generate_chunk_hash(original_file, segment_id)
    
    assert hash1 == hash2
```

2. **Different Inputs Produce Different Hashes**
```python
def test_generate_chunk_hash_different_inputs():
    """Test that different inputs produce different hashes."""
    original_file = "media/1 - Welcome.mp4"
    
    hash1 = generate_chunk_hash(original_file, 0)
    hash2 = generate_chunk_hash(original_file, 1)
    hash3 = generate_chunk_hash("media/2 - Introduction.mp4", 0)
    
    assert hash1 != hash2
    assert hash1 != hash3
```

3. **Hash Format Validation**
```python
def test_generate_chunk_hash_format():
    """Test that the hash has the expected format and length."""
    hash_value = generate_chunk_hash("media/file.mp4", 0)
    
    assert isinstance(hash_value, str)
    assert len(hash_value) == 10
    assert all(c in '0123456789abcdef' for c in hash_value.lower())
```

4. **Special Character Handling**
```python
def test_generate_chunk_hash_special_characters():
    """Test that the function handles special characters in filenames correctly."""
    test_files = [
        "media/file with spaces.mp4",
        "media/file_with_underscore.mp4",
        "media/file-with-dashes.mp4",
        "media/file.with.dots.mp4",
        "media/file@with@special#chars.mp4"
    ]
    
    for file in test_files:
        hash_value = generate_chunk_hash(file, 0)
        assert isinstance(hash_value, str)
```

5. **Invalid Input Handling**
```python
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
```

### 4. Integration
After implementing the function:
1. Update the `send_to_sqs` function to use the new hash as the `chunk_id`
2. Keep the original `segment_id` in the message for reference
3. Update logging to use the new hash-based ID

### 5. Expected Message Format
The SQS message should now look like:
```json
{
    "chunk_id": "a1b2c3d4e5",  // 10-character hash
    "text": "...",
    "start_time": "...",
    "end_time": "...",
    "original_file": "media/1 - Welcome.mp4",
    "segment_id": 0  // Original numeric ID for reference
}
```

## Success Criteria
- All test cases pass
- Hash generation is deterministic
- Hash includes both file name and segment ID information
- Hash is exactly 10 characters long
- Special characters in file names are handled correctly
- Invalid inputs are properly validated
- SQS messages include both the hash-based chunk_id and original segment_id 