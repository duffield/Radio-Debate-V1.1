#!/usr/bin/env python3
"""
Chatterbox TTS Provider
Voice cloning using Chatterbox TTS with debater voice samples
"""

import os
import sys
import warnings
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

# Suppress warnings
warnings.filterwarnings("ignore")

# Import base TTS class  
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tts.base import BaseTTS
from llm.base import DebateResponse

class ChatterboxTTS(BaseTTS):
    """Chatterbox TTS with voice cloning"""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model = None
        self.initialized = False
        self.voice_samples = {}
        self.character_voices = {
            "worried": "debater_1",
            "skeptical": "debater_2", 
            "Truth Seeker": "debater_1",
            "Skeptic": "debater_2"
        }
        
        # Load voice samples
        self._load_voice_samples()
        
        # Set output directory
        self.output_dir = Path("data/audio_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Chatterbox TTS initialized!")
        
    def _load_voice_samples(self):
        """Load voice samples from voice_samples directory"""
        voice_dir = Path(__file__).parent.parent.parent / "voice_samples"
        
        for debater in ["debater_1", "debater_2"]:
            sample_dir = voice_dir / debater
            
            # Look for voice sample files
            for ext in [".mp3", ".wav", ".m4a"]:
                sample_path = sample_dir / f"voice_sample{ext}"
                if sample_path.exists():
                    self.voice_samples[debater] = str(sample_path)
                    print(f"   📂 Found voice sample for {debater}: {sample_path.name}")
                    break
        
        if not self.voice_samples:
            print("   ⚠️  No voice samples found in voice_samples/ directory")
    
    def is_available(self) -> bool:
        """Check if Chatterbox is available"""
        try:
            from chatterbox import ChatterboxTTS as ChatterboxModel
            return True
        except ImportError:
            return False
    
    def initialize(self):
        """Initialize the Chatterbox model"""
        if self.initialized:
            return True
            
        if not self.is_available():
            print("❌ Chatterbox TTS not available")
            return False
            
        try:
            print(f"🔄 Initializing Chatterbox on {self.device}...")
            
            from chatterbox import ChatterboxTTS as ChatterboxModel
            self.model = ChatterboxModel.from_pretrained(device=self.device)
            
            print(f"✅ Chatterbox model loaded on {self.device}")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Chatterbox: {e}")
            
            # If MPS failed, try CPU
            if self.device == "mps":
                print("🔄 Retrying with CPU...")
                self.device = "cpu"
                return self.initialize()
                
            return False
    
    def synthesize(self, debate_response: DebateResponse, output_path: Optional[Path] = None, character: str = None) -> Path:
        """Synthesize speech using voice cloning"""
        if not self.initialized:
            if not self.initialize():
                raise RuntimeError("Failed to initialize Chatterbox TTS")
        
        try:
            # Get voice sample for character
            voice_key = self.character_voices.get(character, "debater_1")
            voice_sample = self.voice_samples.get(voice_key)
            
            if not voice_sample:
                print(f"⚠️  No voice sample for {character} ({voice_key}), using default")
            
            # Generate filename if not provided
            if output_path is None:
                import time
                timestamp = int(time.time() * 1000)
                filename = f"{character}_{timestamp}.wav"
                output_path = self.output_dir / filename
            
            print(f"  🏊 Speaking ({voice_key}): {debate_response.text[:50]}...")
            
            # Generate speech with voice cloning
            params = {
                "text": debate_response.text,
                "temperature": 0.6,
                "exaggeration": 0.0
            }
            
            if voice_sample:
                params["audio_prompt_path"] = voice_sample
            
            # Generate audio
            if self.device == "cpu":
                import torch
                with torch.no_grad():
                    audio = self.model.generate(**params)
            else:
                audio = self.model.generate(**params)
            
            # Save audio to file
            try:
                import soundfile as sf
                
                # Convert to numpy if needed
                if hasattr(audio, 'detach'):
                    audio_np = audio.detach().cpu().numpy()
                else:
                    audio_np = np.array(audio)
                
                # Ensure 1D
                if audio_np.ndim > 1:
                    audio_np = audio_np.flatten()
                
                # Save as WAV
                sf.write(str(output_path), audio_np, 24000, format='WAV')
                print(f"  💾 Saved: {output_path.name}")
                
                return output_path
                
            except Exception as save_error:
                print(f"❌ Could not save audio: {save_error}")
                raise RuntimeError(f"Failed to save audio: {save_error}")
            
        except RuntimeError as e:
            if "FFT" in str(e) and self.device == "mps":
                print(f"❌ FFT error on MPS, switching to CPU...")
                self.device = "cpu"
                self.initialized = False
                return self.synthesize(debate_response, output_path, character)
            else:
                print(f"❌ Speech generation failed: {e}")
                raise RuntimeError(f"Speech synthesis failed: {e}")
        
        except Exception as e:
            print(f"❌ Unexpected error in speech synthesis: {e}")
            raise RuntimeError(f"Speech synthesis failed: {e}")
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about available voices"""
        return {
            "engine": "chatterbox",
            "voice_samples": self.voice_samples,
            "character_mapping": self.character_voices,
            "device": self.device
        }