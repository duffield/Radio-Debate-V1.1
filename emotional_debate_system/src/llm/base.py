from abc import ABC, abstractmethod
from typing import Dict, List
from pydantic import BaseModel, Field

class EmotionMetadata(BaseModel):
    """Emotion metadata structure"""
    name: str
    intensity: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

class DebateResponse(BaseModel):
    """Complete debate response with emotion data"""
    text: str
    emotions: List[EmotionMetadata]
    primary_emotion: str
    valence: float = Field(ge=-1.0, le=1.0)  # Positive/negative
    arousal: float = Field(ge=0.0, le=1.0)   # Calm/excited
    metadata: Dict = Field(default_factory=dict)

class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_with_emotion(self, prompt: str, character: str) -> DebateResponse:
        """Generate text with emotion metadata"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        pass
