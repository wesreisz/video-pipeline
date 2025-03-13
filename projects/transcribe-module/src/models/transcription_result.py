class TranscriptionResult:
    """Data model for transcription results"""
    
    def __init__(self, original_file, transcription_text, timestamp):
        """
        Initialize a new transcription result
        
        Args:
            original_file (str): Path to the original audio file
            transcription_text (str): The transcribed text
            timestamp (str): ISO-formatted timestamp of when the transcription was created
        """
        self.original_file = original_file
        self.transcription_text = transcription_text
        self.timestamp = timestamp
        
    def to_dict(self):
        """
        Convert to dictionary for JSON serialization
        
        Returns:
            dict: Dictionary representation of this result
        """
        return {
            'original_file': self.original_file,
            'transcription_text': self.transcription_text,
            'timestamp': self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create a TranscriptionResult from a dictionary
        
        Args:
            data (dict): Dictionary containing transcription data
            
        Returns:
            TranscriptionResult: New instance populated from the dictionary
        """
        return cls(
            original_file=data.get('original_file'),
            transcription_text=data.get('transcription_text'),
            timestamp=data.get('timestamp')
        ) 