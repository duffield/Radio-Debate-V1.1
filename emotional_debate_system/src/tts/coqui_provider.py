from pathlib import Path
from typing import Optional
import time
import sys

sys.path.append(str(Path(__file__).parent.parent))
from tts.base import BaseTTS
from llm.base import DebateResponse

class CoquiTTS(BaseTTS):
    """Local Coqui TTS provider (simplified version)"""
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        self.model_name = model_name
        print(f"TTS: Using simplified text-to-speech (TTS package not available)")
        print("✅ TTS ready (text-only mode)!")
        self.tts = None  # Simplified mode
    
    def synthesize(self, debate_response: DebateResponse, output_path: Optional[Path] = None, character: str = None) -> Path:
        """Synthesize speech from debate response (simplified - saves text file)"""
        if not self.is_available():
            raise RuntimeError("TTS not available")
        
        # Generate filename
        if output_path is None:
            timestamp = int(time.time())
            filename = f"debate_{timestamp}.txt"
            output_path = Path("data/audio_output") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save text instead of audio (simplified mode)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Text: {debate_response.text}\n")
            f.write(f"Primary Emotion: {debate_response.primary_emotion}\n")
            f.write(f"Valence: {debate_response.valence:.2f}\n")
            f.write(f"Arousal: {debate_response.arousal:.2f}\n")
            f.write(f"Emotions: {', '.join([f'{e.name}({e.intensity:.2f})' for e in debate_response.emotions])}\n")
        
        return output_path
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return True  # Always available in simplified mode
