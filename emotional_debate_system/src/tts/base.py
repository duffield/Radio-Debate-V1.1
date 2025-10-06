from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import sys

sys.path.append(str(Path(__file__).parent.parent))
from llm.base import DebateResponse

class BaseTTS(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    def synthesize(self, debate_response: DebateResponse, output_path: Optional[Path] = None, character: str = None) -> Path:
        """Synthesize speech from debate response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        pass
