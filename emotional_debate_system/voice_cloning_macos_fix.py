#!/usr/bin/env python3
"""
Voice Cloning with macOS Compatibility Fix
Handles FFT operations issue on macOS < 14
"""

import os
import sys
import platform
import warnings
from typing import Optional, Union
import numpy as np
from pathlib import Path

# Suppress warnings
warnings.filterwarnings("ignore")

# Check macOS version for FFT compatibility
def check_macos_fft_compatibility():
    """Check if macOS version supports FFT operations for MPS"""
    try:
        macos_version = platform.mac_ver()[0]
        major_version = int(macos_version.split('.')[0]) if macos_version else 0
        
        if major_version > 0 and major_version < 14:
            print(f"⚠️ macOS {macos_version} detected. FFT operations require macOS 14+")
            print("   Using CPU mode for audio processing...")
            return False
        return True
    except:
        return True  # Assume compatible if can't determine

# Determine device based on compatibility
SUPPORTS_MPS_FFT = check_macos_fft_compatibility()

def get_device():
    """Get the best available device considering compatibility"""
    try:
        import torch
        if torch.backends.mps.is_available() and SUPPORTS_MPS_FFT:
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
    except:
        pass
    return "cpu"

# Set device
DEVICE = get_device()
print(f"🔧 Using device: {DEVICE}")

# If using CPU on Mac, set appropriate torch settings
if DEVICE == "cpu" and platform.system() == "Darwin":
    try:
        import torch
        torch.set_num_threads(8)  # Use multiple threads on CPU
        print("   Optimized CPU settings applied")
    except:
        pass

# Now try to import Chatterbox with the correct device
try:
    from chatterbox import ChatterboxTTS
    CHATTERBOX_AVAILABLE = True
    print("✅ Chatterbox TTS loaded successfully!")
except ImportError as e:
    CHATTERBOX_AVAILABLE = False
    print(f"❌ Chatterbox not available: {e}")


class VoiceCloner:
    """Voice cloner with macOS compatibility"""
    
    def __init__(self, device: str = None):
        self.device = device or DEVICE
        self.model = None
        self.initialized = False
        
    def initialize(self):
        """Initialize the TTS model"""
        if not CHATTERBOX_AVAILABLE:
            print("❌ Chatterbox TTS not available")
            return False
            
        try:
            print(f"🔄 Initializing Chatterbox on {self.device}...")
            
            # Try to initialize with device parameter if supported
            try:
                self.model = ChatterboxTTS(device=self.device)
            except TypeError:
                # If device parameter not supported, try without it
                self.model = ChatterboxTTS()
                
                # Try to move model to device if possible
                if hasattr(self.model, 'to'):
                    self.model = self.model.to(self.device)
                elif hasattr(self.model, 'device'):
                    self.model.device = self.device
            
            print(f"✅ Model initialized on {self.device}")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize model: {e}")
            
            # If MPS failed, try CPU
            if self.device == "mps":
                print("🔄 Retrying with CPU...")
                self.device = "cpu"
                return self.initialize()
                
            return False
    
    def generate_speech(self, text: str, voice_sample: str = None, output_path: str = None):
        """Generate speech with voice cloning"""
        if not self.initialized:
            if not self.initialize():
                return None
                
        try:
            print(f"🎤 Generating speech: '{text[:50]}...'")
            
            # Prepare generation parameters
            params = {
                "text": text,
                "temperature": 0.6,
                "exaggeration": 0.0
            }
            
            # Add voice sample if provided
            if voice_sample and os.path.exists(voice_sample):
                params["audio_prompt_path"] = voice_sample
                print(f"   Using voice sample: {voice_sample}")
            
            # Generate audio
            if self.device == "cpu":
                # CPU mode - may need different parameters
                import torch
                with torch.no_grad():
                    audio = self.model.generate(**params)
            else:
                audio = self.model.generate(**params)
            
            # Save to file if path provided
            if output_path:
                import soundfile as sf
                sf.write(output_path, audio, 24000)
                print(f"✅ Audio saved to: {output_path}")
                
            return audio
            
        except RuntimeError as e:
            if "FFT" in str(e) and self.device == "mps":
                print(f"❌ FFT error on MPS: {e}")
                print("🔄 Switching to CPU mode...")
                self.device = "cpu"
                self.initialized = False
                return self.generate_speech(text, voice_sample, output_path)
            else:
                print(f"❌ Generation failed: {e}")
                return None
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None


def main():
    """Test the voice cloning with macOS compatibility"""
    print("\n" + "="*50)
    print("🧪 Testing Voice Cloning with macOS Compatibility")
    print("="*50 + "\n")
    
    # Check for voice samples
    voice_samples = {
        "debater_1": "voice_samples/debater_1/voice_sample.mp3",
        "debater_2": "voice_samples/debater_2/voice_sample.mp3"
    }
    
    available_samples = {}
    for name, path in voice_samples.items():
        if os.path.exists(path):
            available_samples[name] = path
            print(f"✅ Found {name}: {path}")
        else:
            print(f"⚠️ Missing {name}: {path}")
    
    if not available_samples:
        print("\n⚠️ No voice samples found. Using default voice.")
        
    # Initialize voice cloner
    cloner = VoiceCloner()
    
    if not cloner.initialize():
        print("\n❌ Failed to initialize voice cloner")
        
        # Fallback to system TTS
        print("\n🔄 Falling back to system TTS...")
        text = "Hello! This is a test of the voice synthesis system."
        os.system(f'say "{text}"')
        print("✅ System TTS playback complete")
        return
    
    # Test generation
    test_texts = [
        "Hello! This is a test of the voice cloning system.",
        "The weather today is quite pleasant.",
        "Technology continues to advance at a rapid pace."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        
        # Use first available sample if any
        voice_sample = list(available_samples.values())[0] if available_samples else None
        
        # Generate audio
        audio = cloner.generate_speech(
            text=text,
            voice_sample=voice_sample,
            output_path=f"test_output_{i}.wav"
        )
        
        if audio is not None:
            print(f"✅ Successfully generated audio {i}")
            
            # Try to play it
            try:
                import sounddevice as sd
                sd.play(audio, samplerate=24000)
                sd.wait()
                print("   Playback complete")
            except:
                print("   (Playback not available, audio saved to file)")
        else:
            print(f"❌ Failed to generate audio {i}")
    
    print("\n" + "="*50)
    print("✅ Testing complete!")
    print("="*50)


if __name__ == "__main__":
    main()