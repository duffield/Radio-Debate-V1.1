from pathlib import Path
from typing import Optional
import time
import subprocess
import sys

sys.path.append(str(Path(__file__).parent.parent))
from tts.base import BaseTTS
from llm.base import DebateResponse

class MacOSTTS(BaseTTS):
    """macOS system TTS provider using 'say' command"""
    
    def __init__(self, voice: str = "Samantha"):
        self.voice = voice
        print(f"TTS: Using macOS system voice '{voice}'")
        print("✅ TTS ready!")
    
    def synthesize(self, debate_response: DebateResponse, output_path: Optional[Path] = None, character: str = None) -> Path:
        """Synthesize speech using macOS 'say' command"""
        if not self.is_available():
            raise RuntimeError("TTS not available")
        
        # Generate filename
        if output_path is None:
            timestamp = int(time.time())
            filename = f"debate_{timestamp}.aiff"
            output_path = Path("data/audio_output") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Select voice based on character
        voice = self._get_character_voice(character)
        
        # Use macOS 'say' command to speak directly AND save to file
        try:
            # Speak directly (real-time)
            print(f"  🔊 Speaking ({voice}): {debate_response.text[:50]}...")
            speak_cmd = ["say", "-v", voice, debate_response.text]
            subprocess.run(speak_cmd, check=True)
            
            # Also save to file for later playback
            save_cmd = [
                "say",
                "-v", voice,
                "-o", str(output_path),
                debate_response.text
            ]
            subprocess.run(save_cmd, check=True, capture_output=True)
            print(f"  💾 Saved audio: {output_path.name}")
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ TTS error: {e}")
            # Fallback: save as text file
            text_path = output_path.with_suffix('.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"Text: {debate_response.text}\n")
                f.write(f"Primary Emotion: {debate_response.primary_emotion}\n")
                f.write(f"Valence: {debate_response.valence:.2f}\n")
                f.write(f"Arousal: {debate_response.arousal:.2f}\n")
            return text_path
        
        return output_path
    
    def is_available(self) -> bool:
        """Check if macOS 'say' command is available"""
        try:
            # Test with a simple command that should work
            result = subprocess.run(["say", "-v", "?"], capture_output=True, check=True)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_character_voice(self, character: str) -> str:
        """Get voice for specific character"""
        character_voices = {
            "worried": "Ralph",       # Deep, paranoid male (available)
            "skeptical": "Samantha",  # Clear, logical female
            "truth_seeker": "Ralph",  # Deep, paranoid male (available)
            "skeptic": "Samantha",    # Clear, logical female
        }
        
        if character and character in character_voices:
            return character_voices[character]
        
        return self.voice  # Default voice
    
    def list_voices(self):
        """List available voices"""
        try:
            result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return "No voices available"
