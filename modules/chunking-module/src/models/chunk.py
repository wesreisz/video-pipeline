from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Chunk:
    """Represents a chunk of media content."""
    
    start_time: float
    end_time: float
    content: str
    index: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkingResult:
    """Represents the result of a chunking operation."""
    
    original_file: str
    media_type: str
    timestamp: str
    job_name: str
    chunks: List[Chunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the chunking result to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the chunking result
        """
        return {
            "original_file": self.original_file,
            "media_type": self.media_type,
            "timestamp": self.timestamp,
            "job_name": self.job_name,
            "chunks": [
                {
                    "start_time": chunk.start_time,
                    "end_time": chunk.end_time,
                    "content": chunk.content,
                    "index": chunk.index,
                    "metadata": chunk.metadata
                }
                for chunk in self.chunks
            ],
            "metadata": self.metadata
        } 