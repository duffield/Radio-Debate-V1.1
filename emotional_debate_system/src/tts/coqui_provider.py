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
