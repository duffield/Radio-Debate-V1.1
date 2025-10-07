#!/usr/bin/env python3
"""
Simple TTS Debate System using Coqui TTS
Uses the prepared voice models for voice cloning
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional
import tempfile
import subprocess

# Try to import TTS
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    print("✅ Coqui TTS loaded successfully!")
except ImportError:
    TTS_AVAILABLE = False
    print("❌ Coqui TTS not available")

class SimpleTTSDebater:
    """Simple TTS debater using voice cloning"""
    
    def __init__(self, name: str, voice_sample_path: str):
        self.name = name
        self.voice_sample_path = voice_sample_path
        self.tts = None
        
        print(f"🎭 Initializing {name}")
        print(f"   Voice sample: {voice_sample_path}")
        
        if TTS_AVAILABLE:
            try:
                # Use CPU to avoid CUDA issues - YourTTS supports voice cloning
                print("   Loading YourTTS model for voice cloning (CPU mode)...")
                self.tts = TTS(
                    model_name="tts_models/multilingual/multi-dataset/your_tts",
                    gpu=False  # Force CPU mode
                )
                print("✅ TTS model loaded successfully!")
            except Exception as e:
                print(f"❌ Failed to load TTS: {e}")
                self.tts = None
    
    def speak(self, text: str, play_immediately: bool = True) -> bool:
        """Generate and play speech"""
        if not self.tts:
            print(f"❌ {self.name}: TTS not available, falling back to system TTS")
            return self._system_tts_fallback(text)
        
        try:
            print(f"🎤 {self.name}: Generating '{text[:50]}...'")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Check if voice sample exists and use it for cloning
            if os.path.exists(self.voice_sample_path):
                print(f"   Using voice sample for cloning: {Path(self.voice_sample_path).name}")
                self.tts.tts_to_file(
                    text=text,
                    file_path=temp_path,
                    speaker_wav=self.voice_sample_path,
                    language="en"  # Required for YourTTS multilingual model
                )
            else:
                print("   Using default voice (no sample found)")
                self.tts.tts_to_file(
                    text=text,
                    file_path=temp_path,
                    language="en"
                )
            
            # Play the generated audio
            if play_immediately and os.path.exists(temp_path):
                print(f"🔊 {self.name}: Playing generated speech...")
                # Use Python's sounddevice to play the audio directly
                try:
                    import soundfile as sf
                    import sounddevice as sd
                    
                    # Read the audio file
                    audio_data, samplerate = sf.read(temp_path)
                    
                    # Play using sounddevice (should work with any audio interface)
                    print(f"   Playing via sounddevice...")
                    sd.play(audio_data, samplerate)
                    sd.wait()  # Wait for playback to finish
                    
                except ImportError:
                    print(f"   ⚠️ sounddevice not available, trying afplay...")
                    try:
                        subprocess.run(["afplay", temp_path], check=False, timeout=30)
                    except:
                        print(f"   ⚠️ Could not play audio file")
                except Exception as e:
                    print(f"   ⚠️ Audio playback failed: {e}")
                    # Fallback: just show that we generated it
                    print(f"   🎧 Generated TTS audio saved to: {temp_path}")
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ {self.name}: TTS generation failed: {e}")
            return self._system_tts_fallback(text)
    
    def _system_tts_fallback(self, text: str) -> bool:
        """Fallback to system TTS"""
        try:
            voice_map = {
                "Truth Seeker": "Ralph",    # Deep, paranoid voice
                "Skeptic": "Samantha"       # Clear, logical voice
            }
            voice = voice_map.get(self.name, "Alex")
            
            print(f"🔊 {self.name}: Speaking with system voice ({voice})")
            subprocess.run(["say", "-v", voice, text], check=True)
            return True
            
        except Exception as e:
            print(f"❌ {self.name}: System TTS also failed: {e}")
            return False

class SimpleTTSDebateSystem:
    """Simple debate system with TTS voice cloning"""
    
    def __init__(self):
        print("\n🎭 Simple TTS Debate System")
        print("=" * 50)
        
        # Initialize debaters with their voice samples
        self.debater_1 = SimpleTTSDebater(
            "Truth Seeker",
            "voice_samples/debater_1/voice_sample.mp3"
        )
        
        self.debater_2 = SimpleTTSDebater(
            "Skeptic", 
            "voice_samples/debater_2/voice_sample.mp3"
        )
        
        print("\n✅ Debaters initialized!")
    
    def run_debate(self, topic: str, rounds: int = 2):
        """Run a debate with TTS voice cloning"""
        print(f"\n🎭 Starting debate: '{topic}'")
        print("=" * 50)
        
        # Sample debate statements
        debate_statements = [
            # Round 1
            [
                f"I'm deeply concerned about {topic.lower()}. There are patterns here that people need to understand, connections that go deeper than most realize.",
                f"Let's stick to facts and evidence. What specific, verifiable information do you have to support your claims about {topic.lower()}?"
            ],
            # Round 2
            [
                "The evidence is all around us if you know where to look. The mainstream sources won't tell you the real story.",
                "That's exactly the problem - vague claims about 'evidence everywhere' without providing any concrete, credible sources. Show me peer-reviewed research or official documentation."
            ],
            # Additional rounds can be added here
        ]
        
        debaters = [self.debater_1, self.debater_2]
        
        for round_num in range(min(rounds, len(debate_statements))):
            print(f"\n📊 Round {round_num + 1}/{rounds}")
            print("-" * 40)
            
            statements = debate_statements[round_num]
            
            for i, statement in enumerate(statements):
                debater = debaters[i]
                print(f"\n[{debater.name}]: {statement}")
                
                # Generate and play speech
                success = debater.speak(statement)
                if not success:
                    print("   (Speech generation failed)")
                
                # Pause between debaters
                time.sleep(1)
            
            print("\n" + "=" * 50)
        
        print("\n🏁 Debate complete!")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple TTS Debate System")
    parser.add_argument('--topic', type=str, 
                       default="artificial intelligence regulation",
                       help="Debate topic")
    parser.add_argument('--rounds', type=int, default=2,
                       help="Number of debate rounds")
    
    args = parser.parse_args()
    
    try:
        system = SimpleTTSDebateSystem()
        system.run_debate(topic=args.topic, rounds=args.rounds)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Debate interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()