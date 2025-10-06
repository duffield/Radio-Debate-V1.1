#!/usr/bin/env python3
"""
M1 Max Optimized Two-Debater Voice Cloning System
Now with full MPS acceleration support on macOS 14+
"""

import os
import sys
import platform
import warnings
from typing import Optional, Dict, List
import numpy as np
from pathlib import Path
import time
import threading

# Suppress warnings
warnings.filterwarnings("ignore")

try:
    from chatterbox import ChatterboxTTS
    CHATTERBOX_AVAILABLE = True
    print("✅ Chatterbox TTS loaded successfully!")
except ImportError as e:
    CHATTERBOX_AVAILABLE = False
    print(f"❌ Chatterbox not available: {e}")

def get_device():
    """Get the best available device"""
    try:
        import torch
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
    except:
        pass
    return "cpu"

class M1OptimizedVoiceDebater:
    """M1 Max optimized voice cloning debater"""
    
    def __init__(self, name: str, voice_sample_path: str, device: str = None):
        self.name = name
        self.voice_sample_path = voice_sample_path
        self.device = device or get_device()
        self.model = None
        self.initialized = False
        self.generation_cache = {}
        
        print(f"🎭 Initializing {name} debater")
        print(f"   Voice sample: {voice_sample_path}")
        print(f"   Device: {self.device}")
    
    def initialize(self) -> bool:
        """Initialize the TTS model"""
        if not CHATTERBOX_AVAILABLE:
            print(f"❌ {self.name}: Chatterbox TTS not available")
            return False
            
        if not os.path.exists(self.voice_sample_path):
            print(f"❌ {self.name}: Voice sample not found: {self.voice_sample_path}")
            return False
            
        try:
            print(f"🔄 {self.name}: Loading Chatterbox model on {self.device}...")
            self.model = ChatterboxTTS.from_pretrained(device=self.device)
            print(f"✅ {self.name}: Model ready on {self.device}")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ {self.name}: Failed to initialize: {e}")
            return False
    
    def pre_generate_speech(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """Pre-generate speech for multiple texts (optimization)"""
        if not self.initialized:
            return {}
            
        cache = {}
        print(f"🔄 {self.name}: Pre-generating {len(texts)} speeches...")
        
        for i, text in enumerate(texts, 1):
            try:
                print(f"   {i}/{len(texts)}: '{text[:50]}...'")
                audio = self._generate_audio(text)
                if audio is not None:
                    cache[text] = audio
                    print(f"   ✅ Pre-generated {i}")
                else:
                    print(f"   ❌ Failed {i}")
                    
            except Exception as e:
                print(f"   ❌ Error generating {i}: {e}")
                
        print(f"✅ {self.name}: Pre-generated {len(cache)}/{len(texts)} speeches")
        self.generation_cache.update(cache)
        return cache
    
    def speak(self, text: str, play_immediately: bool = True, save_path: str = None) -> Optional[np.ndarray]:
        """Generate and optionally play speech"""
        if not self.initialized:
            if not self.initialize():
                return None
        
        # Check cache first
        if text in self.generation_cache:
            print(f"🎯 {self.name}: Using cached audio for '{text[:50]}...'")
            audio = self.generation_cache[text]
        else:
            audio = self._generate_audio(text)
            if audio is not None:
                self.generation_cache[text] = audio
        
        if audio is None:
            return None
            
        # Save to file if requested
        if save_path:
            self._save_audio(audio, save_path)
        
        # Play immediately if requested
        if play_immediately:
            self._play_audio(audio, save_path or f"temp_{self.name}_{int(time.time())}.wav")
            
        return audio
    
    def _generate_audio(self, text: str) -> Optional[np.ndarray]:
        """Generate audio for given text"""
        try:
            print(f"🎤 {self.name}: Generating '{text[:50]}...'")
            
            audio = self.model.generate(
                text=text,
                audio_prompt_path=self.voice_sample_path,
                temperature=0.6,
                exaggeration=0.0
            )
            
            return audio
            
        except Exception as e:
            print(f"❌ {self.name}: Generation failed: {e}")
            return None
    
    def _save_audio(self, audio: np.ndarray, path: str):
        """Save audio to file"""
        try:
            import soundfile as sf
            # Ensure audio is in the right format
            if hasattr(audio, 'numpy'):
                audio_np = audio.detach().cpu().numpy()
            else:
                audio_np = np.array(audio)
            
            if audio_np.ndim > 1:
                audio_np = audio_np.flatten()
                
            sf.write(path, audio_np, 24000, format='WAV')
            print(f"💾 {self.name}: Saved to {path}")
            
        except Exception as e:
            print(f"⚠️ {self.name}: Could not save audio: {e}")
    
    def _play_audio(self, audio: np.ndarray, temp_path: str):
        """Play audio using system audio"""
        try:
            # Save temporarily if needed
            if not os.path.exists(temp_path):
                self._save_audio(audio, temp_path)
            
            # Play using afplay (macOS)
            os.system(f"afplay {temp_path}")
            
            # Clean up temporary file if it was created
            if temp_path.startswith("temp_"):
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ {self.name}: Playback failed: {e}")


class TwoDebaterSystem:
    """Two-debater voice cloning system"""
    
    def __init__(self):
        self.device = get_device()
        self.debater_1 = None
        self.debater_2 = None
        
        print("\n" + "="*60)
        print("🎭 M1 Max Optimized Two-Debater Voice System")
        print(f"🔧 Device: {self.device}")
        print("="*60)
    
    def setup_debaters(self):
        """Set up the two debaters"""
        # Define voice sample paths
        voice_samples = {
            "debater_1": "voice_samples/debater_1/voice_sample.mp3",
            "debater_2": "voice_samples/debater_2/voice_sample.mp3"
        }
        
        # Check availability
        missing_samples = []
        for name, path in voice_samples.items():
            if os.path.exists(path):
                print(f"✅ Found {name}: {path}")
            else:
                print(f"⚠️ Missing {name}: {path}")
                missing_samples.append(name)
        
        if missing_samples:
            print(f"\n⚠️ Missing voice samples for: {', '.join(missing_samples)}")
            print("   Please record voice samples and place them in the voice_samples/ directory")
            return False
        
        # Initialize debaters
        self.debater_1 = M1OptimizedVoiceDebater(
            name="Debater 1 (Progressive)", 
            voice_sample_path=voice_samples["debater_1"],
            device=self.device
        )
        
        self.debater_2 = M1OptimizedVoiceDebater(
            name="Debater 2 (Conservative)", 
            voice_sample_path=voice_samples["debater_2"],
            device=self.device
        )
        
        # Initialize both debaters
        success_1 = self.debater_1.initialize()
        success_2 = self.debater_2.initialize()
        
        return success_1 and success_2
    
    def run_sample_debate(self):
        """Run a sample debate between the two voices"""
        if not self.debater_1 or not self.debater_2:
            print("❌ Debaters not set up. Run setup_debaters() first.")
            return
        
        # Sample debate topics and responses
        debate_script = [
            ("debater_1", "Good morning! Today we're discussing the future of artificial intelligence and its impact on society."),
            ("debater_2", "Thank you. I believe we must proceed with extreme caution when it comes to AI development."),
            ("debater_1", "While caution is important, we shouldn't let fear prevent us from realizing AI's incredible potential to solve global challenges."),
            ("debater_2", "But what about job displacement? AI could eliminate millions of jobs without creating adequate replacements."),
            ("debater_1", "History shows that technological revolutions create new types of work. We should focus on education and adaptation."),
            ("debater_2", "That's an optimistic view, but the pace of AI development far exceeds our ability to retrain workers effectively."),
        ]
        
        print("\n" + "🎪 STARTING DEBATE 🎪".center(60))
        print("="*60)
        
        # Pre-generate all speeches for optimization
        texts_1 = [text for speaker, text in debate_script if speaker == "debater_1"]
        texts_2 = [text for speaker, text in debate_script if speaker == "debater_2"]
        
        print("\n🚀 Pre-generating speeches for optimal performance...")
        
        # Pre-generate in parallel threads for maximum M1 efficiency
        def pre_gen_1():
            self.debater_1.pre_generate_speech(texts_1)
        
        def pre_gen_2():
            self.debater_2.pre_generate_speech(texts_2)
        
        thread_1 = threading.Thread(target=pre_gen_1)
        thread_2 = threading.Thread(target=pre_gen_2)
        
        thread_1.start()
        thread_2.start()
        
        thread_1.join()
        thread_2.join()
        
        print("\n✅ Pre-generation complete! Starting debate...\n")
        
        # Run the actual debate
        for i, (speaker, text) in enumerate(debate_script, 1):
            print(f"\n{'='*60}")
            debater = self.debater_1 if speaker == "debater_1" else self.debater_2
            
            print(f"🎤 {debater.name}:")
            print(f"   \"{text}\"")
            print(f"{'='*60}")
            
            # Generate and play speech
            debater.speak(
                text=text,
                play_immediately=True,
                save_path=f"debate_output_{i:02d}_{speaker}.wav"
            )
            
            # Short pause between speakers
            time.sleep(1)
        
        print("\n" + "🏁 DEBATE COMPLETE! 🏁".center(60))
        print("="*60)
        
        # List generated files
        print("\n📁 Generated audio files:")
        for file in sorted(Path(".").glob("debate_output_*.wav")):
            print(f"   {file}")
    
    def interactive_mode(self):
        """Interactive mode for custom debates"""
        if not self.debater_1 or not self.debater_2:
            print("❌ Debaters not set up. Run setup_debaters() first.")
            return
        
        print("\n" + "🎮 INTERACTIVE MODE 🎮".center(60))
        print("="*60)
        print("Type text for each debater, or 'quit' to exit")
        print("Commands: 'switch' to change speaker, 'quit' to exit")
        print("="*60)
        
        current_debater = self.debater_1
        turn = 1
        
        while True:
            print(f"\n🎤 {current_debater.name} (Turn {turn}):")
            user_input = input(">>> ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'switch':
                current_debater = self.debater_2 if current_debater == self.debater_1 else self.debater_1
                continue
            elif user_input:
                current_debater.speak(
                    text=user_input,
                    play_immediately=True,
                    save_path=f"interactive_{turn:03d}_{current_debater.name.replace(' ', '_')}.wav"
                )
                
                # Switch to other debater
                current_debater = self.debater_2 if current_debater == self.debater_1 else self.debater_1
                turn += 1
        
        print("\n👋 Interactive session ended!")


def main():
    """Main function"""
    print("🚀 Initializing M1 Max Two-Debater Voice System...")
    
    system = TwoDebaterSystem()
    
    if not system.setup_debaters():
        print("\n❌ Failed to set up debaters. Please check voice samples and try again.")
        return
    
    print("\n✅ System ready!")
    print("\nChoose an option:")
    print("1. Run sample debate")
    print("2. Interactive mode")
    print("3. Exit")
    
    while True:
        choice = input("\n> ").strip()
        
        if choice == "1":
            system.run_sample_debate()
        elif choice == "2":
            system.interactive_mode()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("Please choose 1, 2, or 3")


if __name__ == "__main__":
    main()