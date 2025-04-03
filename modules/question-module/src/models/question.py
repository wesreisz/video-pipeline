from typing import Optional
from dataclasses import dataclass

@dataclass
class Question:
    """
    Represents a question to be processed.
    """
    question_id: str
    content: str
    context: Optional[str] = None
    metadata: Optional[dict] = None 