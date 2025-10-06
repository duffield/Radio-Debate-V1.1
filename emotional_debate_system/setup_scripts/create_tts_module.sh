#!/bin/bash

echo "🔊 Creating TTS module..."

# Create base TTS interface
cat > src/tts/base.py << 'EOF'
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import sys

sys.path.append(str(Path(__file__).parent.parent))
from llm.base import DebateResponse

class BaseTTS(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    def synthesize(self, debate_response: DebateResponse, output_path: Optional[Path] = None) -> Path:
        """Synthesize speech from debate response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        pass
EOF

echo "✅ Created src/tts/base.py"

# Create Coqui TTS provider
cat > src/tts/coqui_provider.py << 'EOF'
from TTS.api import TTS
from pathlib import Path
from typing import Optional
import time
import sys

sys.path.append(str(Path(__file__).parent.parent))
from tts.base import BaseTTS
from llm.base import DebateResponse

class CoquiTTS(BaseTTS):
    """Local Coqui TTS provider"""
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        self.model_name = model_name
        print(f"Loadi