#!/usr/bin/env python3
"""
Simple M1 Optimized Voice System
Alternative approach using stable TTS libraries that work well on M1 Max
"""

import os
import sys
import time
import tempfile
import warnings
from pathlib import Path
from typing import List, Optional, Dict
import numpy as np

# Check if we're on M1 Mac and have the right dependencies
try:
    import torch
    import sounddevice as sd
    import soundfile as sf
    import psutil
    from pydub import AudioSegment
    print("✅ Core dependencies loaded successfully!")
    print("✅ MP3 support enabled!")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Please ensure you've run the setup script and activated the environment")
    sys.exit(1)

warnings.filterwarnings("ignore", category=UserWarning)


class SimpleM1VoiceSystem:
    """
    Simple M1 Max optimized voice system using macOS built-in TTS
    This is a fallback approach when advanced voice cloning libraries have issues
    """
    
    def __init__(self):
        self.device = self._get_optimal_device()
        self.setup_audio()
        
        print("🎭 Simple M1 Voice System initialized")
        print(f"   Device: {self.device}")
        
    def _get_optimal_device(self) -> str:
        """Determine best device for M1 Max"""
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return "mps"
        else:
            print("⚠️  MPS not available, using CPU")
            return "cpu"
    
    def setup_audio(self):
        """Configure audio settings for M1 Max"""
        sd.default.samplerate = 22050
        sd.default.channels = 1
        sd.default.dtype = 'float32'
        
        # Set environment variables for M1 optimization
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        os.environ['OMP_NUM_THREADS'] = '8'
    
    def test_mps_performance(self):
        """Test MPS performance with tensor operations"""
        print("🔄 Testing M1 MPS performance...")
        
        if self.device != "mps":
            print("⚠️  MPS not available for testing")
            return False
        
        try:
            device = torch.device("mps")
            
            # Test tensor operations
            start_time = time.time()
            x = torch.randn(1000, 1000, device=device)
            y = torch.randn(1000, 1000, device=device)
            result = torch.mm(x, y)
            
            elapsed = time.time() - start_time
            print(f"✅ MPS tensor operations: {elapsed:.3f}s")
            
            # Clear cache
            torch.mps.empty_cache()
            return True
            
        except Exception as e:
            print(f"❌ MPS test failed: {e}")
            return False
    
    def record_voice_sample(self, duration: int = 10, filename: str = "voice_sample.wav") -> bool:
        """Record a voice sample for future use"""
        print(f"🎤 Recording {duration} seconds of audio...")
        print("   Speak clearly and naturally")
        print("   3... 2... 1... Recording!")
        
        try:
            # Record audio
            audio_data = sd.rec(
                int(duration * 22050),
                samplerate=22050,
                channels=1,
                dtype=np.float32
            )
            
            # Countdown
            for i in range(duration, 0, -1):
                print(f"   {i}s remaining...", end='\r')
                time.sleep(1)
            
            sd.wait()
            print(f"\n✅ Recording complete!")
            
            # Save audio
            sf.write(filename, audio_data, 22050)
            print(f"💾 Saved as: {filename}")
            
            return True
            
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return False
    
    def use_macos_tts(self, text: str, voice: str = "Alex") -> bool:
        """Use macOS built-in text-to-speech"""
        try:
            # Use macOS 'say' command with specified voice
            cmd = f'say -v "{voice}" "{text}"'
            os.system(cmd)
            return True
        except Exception as e:
            print(f"❌ macOS TTS failed: {e}")
            return False
    def convert_audio_to_wav(self, filename: str) -> str:
        """Convert MP3/M4A files to WAV format for processing"""
        file_path = Path(filename)
        
        # If already WAV, return as-is
        if file_path.suffix.lower() == '.wav':
            return filename
        
        try:
            # Convert using pydub
            print(f"🔄 Converting {file_path.suffix} to WAV...")
            audio = AudioSegment.from_file(filename)
            
            # Convert to WAV format
            wav_filename = str(file_path.with_suffix('.wav'))
            audio.export(wav_filename, format='wav', parameters=["-ar", "22050", "-ac", "1"])
            
            print(f"✅ Converted to: {wav_filename}")
            return wav_filename
            
        except Exception as e:
            print(f"❌ Audio conversion failed: {e}")
            return filename
    
    def play_audio_file(self, filename: str) -> bool:
        """Play an audio file (supports WAV, MP3, M4A)"""
        try:
            if not os.path.exists(filename):
                print(f"❌ Audio file not found: {filename}")
                return False
            
            # Convert to WAV if needed
            wav_file = self.convert_audio_to_wav(filename)
            
            # Load and play audio
            data, samplerate = sf.read(wav_file)
            sd.play(data, samplerate)
            sd.wait()
            return True
            
        except Exception as e:
            print(f"❌ Playback failed: {e}")
            # Try alternative method with pydub
            try:
                print("Trying alternative playback method...")
                audio = AudioSegment.from_file(filename)
                # Convert to wav data
                wav_data = audio.export(format='wav')
                data, samplerate = sf.read(wav_data)
                sd.play(data, samplerate)
                sd.wait()
                return True
            except Exception as e2:
                print(f"❌ Alternative playback also failed: {e2}")
                return False
    def run_installation_demo(self):
        """Run a simplified installation demo"""
        print("\n🎭 SIMPLIFIED EMOTIONAL DEBATE DEMO")
        print("=" * 50)
        
        # Sample debate statements (simplified)
        statements = [
            "Welcome to this exploration of identity and artificial intelligence.",
            "I am speaking to you through this synthesized voice.",
            "What defines human identity in an age of artificial minds?",
            "Can a machine truly understand the weight of human emotion?",
            "Thank you for participating in this experience."
        ]
        
        print("🎯 This demo uses macOS built-in voices as a fallback")
        print("   In the full system, this would use your cloned voice")
        
        input("Press Enter to begin the demo...")
        
        print("\n🎭 Starting Emotional Debate...")
        
        for i, statement in enumerate(statements, 1):
            print(f"\n[{i}/{len(statements)}] 🗣️  \"{statement}\"")
            
            # Use macOS TTS
            self.use_macos_tts(statement, voice="Alex")
            
            # Pause between statements
            if i < len(statements):
                time.sleep(1.5)
        
        print("\n🎭 Demo complete!")
        print("   In the full system, this would use advanced voice cloning")


def check_system_requirements():
    """Check if system meets requirements for voice cloning"""
    print("🔍 Checking System Requirements")
    print("=" * 40)
    
    checks = []
    
    # Check macOS version
    try:
        import subprocess
        result = subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True)
        macos_version = result.stdout.strip()
        print(f"macOS version: {macos_version}")
        checks.append(("macOS", True))
    except:
        checks.append(("macOS version check", False))
    
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version.major == 3 and python_version.minor >= 9
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    checks.append(("Python 3.9+", python_ok))
    
    # Check PyTorch and MPS
    try:
        mps_available = torch.backends.mps.is_available()
        mps_built = torch.backends.mps.is_built()
        print(f"PyTorch version: {torch.__version__}")
        print(f"MPS available: {mps_available}")
        print(f"MPS built: {mps_built}")
        checks.append(("PyTorch MPS", mps_available and mps_built))
    except:
        checks.append(("PyTorch MPS", False))
    
    # Check audio libraries
    audio_ok = True
    try:
        import sounddevice
        import soundfile
        print("Audio libraries: sounddevice, soundfile ✓")
    except ImportError:
        audio_ok = False
        print("Audio libraries: Missing")
    checks.append(("Audio libraries", audio_ok))
    
    # Check system resources
    try:
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"Total RAM: {memory_gb:.1f} GB")
        checks.append(("Memory (16GB+)", memory_gb >= 16))
    except:
        checks.append(("Memory check", False))
    
    print("\n📊 System Check Results:")
    all_good = True
    for check_name, status in checks:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {check_name}")
        if not status:
            all_good = False
    
    return all_good


def main():
    """Main function"""
    print("🎭 Simple M1 Voice System")
    print("=" * 30)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n⚠️  Some system requirements not met")
        print("   The demo will still run but performance may be limited")
        
        choice = input("\nContinue anyway? (y/n): ")
        if choice.lower() != 'y':
            return
    
    # Initialize system
    voice_system = SimpleM1VoiceSystem()
    
    # Test MPS performance
    voice_system.test_mps_performance()
    
    print("\n🎯 Available Options:")
    print("1. Record voice sample")
    print("2. Run installation demo")
    print("3. Test audio playback")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                duration = input("Recording duration in seconds (default 10): ").strip()
                try:
                    duration = int(duration) if duration else 10
                except ValueError:
                    duration = 10
                
                voice_system.record_voice_sample(duration)
            
            elif choice == "2":
                voice_system.run_installation_demo()
            
            elif choice == "3":
                filename = input("Audio file to play (default: voice_sample.wav): ").strip()
                filename = filename if filename else "voice_sample.wav"
                voice_system.play_audio_file(filename)
            
            elif choice == "4":
                print("👋 Goodbye!")
                break
            
            else:
                print("Please select 1-4")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()