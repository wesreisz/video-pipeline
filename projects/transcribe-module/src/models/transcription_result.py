class TranscriptionResult:
    """Data model for transcription results"""
    
    def __init__(self, original_file, transcription_text, timestamp, job_name=None, media_type='audio', segments=None):
        """
        Initialize a new transcription result
        
        Args:
            original_file (str): Path to the original audio or video file
            transcription_text (str): The transcribed text
            timestamp (str): ISO-formatted timestamp of when the transcription was created
            job_name (str, optional): AWS Transcribe job name
            media_type (str, optional): Type of media ('audio' or 'video'), defaults to 'audio'
            segments (list, optional): List of time-stamped segments from the transcription
        """
        self.original_file = original_file
        self.transcription_text = transcription_text
        self.timestamp = timestamp
        self.job_name = job_name
        self.media_type = media_type
        self.segments = segments or []
        
    def to_dict(self):
        """
        Convert to dictionary for JSON serialization
        
        Returns:
            dict: Dictionary representation of this result
        """
        result = {
            'original_file': self.original_file,
            'transcription_text': self.transcription_text,
            'timestamp': self.timestamp,
            'media_type': self.media_type
        }
        
        # Add job_name if it exists
        if self.job_name:
            result['job_name'] = self.job_name
        
        # Only add segments if they exist and the list is not empty
        if self.segments:
            result['segments'] = self.segments
            
        return result
        
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
            timestamp=data.get('timestamp'),
            job_name=data.get('job_name'),
            media_type=data.get('media_type', 'audio'),  # Default to 'audio' for backward compatibility
            segments=data.get('segments', [])
        ) 