#!/usr/bin/env python3
"""
Two-Voice Debate Demo
Uses two different macOS voices to simulate a debate between cloned voices
This is a preview of what the full voice cloning system will sound like
"""

import os
import sys
import time
import warnings
from typing import List, Tuple

# Try to import required libraries
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


class TwoVoiceDebateSystem:
    """
    Two-voice debate system using macOS built-in TTS
    Simulates what the voice cloning system will sound like
    """
    
    def __init__(self):
        self.device = self._get_optimal_device()
        self.setup_audio()
        
        # Available voice pairs for debates
        self.voice_pairs = [
            ("Samantha", "Daniel"),  # American female vs British male
            ("Karen", "Reed (English (U.S.))"),   # Australian vs American
            ("Moira", "Albert"),     # Irish vs American
            ("Kathy", "Fred"),       # Different American voices
        ]
        
        print("🎭 Two-Voice Debate System initialized")
        print(f"   Device: {self.device}")
    
    def _get_optimal_device(self) -> str:
        """Get optimal device for M1 Max"""
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return "mps"
        else:
            print("⚠️  MPS not available, using CPU")
            return "cpu"
    
    def setup_audio(self):
        """Setup audio for M1 optimization"""
        # M1 optimization
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        os.environ['OMP_NUM_THREADS'] = '8'
    
    def speak_as_debater(self, text: str, voice: str, debater_name: str):
        """Make a debater speak using macOS TTS"""
        print(f"\n🗣️  {debater_name} ({voice}): \"{text}\"")
        try:
            cmd = f'say -v "{voice}" "{text}"'
            os.system(cmd)
            return True
        except Exception as e:
            print(f"❌ Speech failed for {debater_name}: {e}")
            return False
    
    def run_ai_debate(self, voice_pair: Tuple[str, str] = None):
        """Run an AI ethics debate between two voices"""
        if not voice_pair:
            voice_pair = self.voice_pairs[0]  # Default to Samantha vs Daniel
        
        voice_1, voice_2 = voice_pair
        
        print("\n🎭 AI ETHICS DEBATE")
        print("=" * 50)
        print(f"🎯 Topic: The Future of Artificial Intelligence")
        print(f"   Debater 1 ({voice_1}): Pro-AI optimist")
        print(f"   Debater 2 ({voice_2}): Cautious realist")
        print("=" * 50)
        
        # Debate script
        debate_rounds = [
            (1, voice_1, "Debater 1", "Good evening everyone. I believe artificial intelligence represents humanity's greatest opportunity to solve our most pressing challenges, from climate change to disease."),
            (2, voice_2, "Debater 2", "Thank you. While I appreciate AI's potential, I believe we're moving too quickly without proper safeguards. We must consider the risks to employment, privacy, and human agency."),
            (1, voice_1, "Debater 1", "But consider this: every major technological revolution initially displaced workers, yet ultimately created more jobs than it destroyed. The printing press, the steam engine, the internet - all followed this pattern."),
            (2, voice_2, "Debater 2", "That's true historically, but AI is fundamentally different. It's not just automating physical tasks - it's replicating cognitive abilities that we thought were uniquely human."),
            (1, voice_1, "Debater 1", "Exactly! And that's what makes it so exciting. AI can handle routine cognitive work, freeing humans to focus on creativity, empathy, and complex problem-solving that truly matter."),
            (2, voice_2, "Debater 2", "But who decides what's 'routine'? And what happens to the human skills we don't practice? We risk becoming dependent on systems we don't fully understand or control."),
            (1, voice_1, "Debater 1", "These are valid concerns, but the solution isn't to halt progress. We need robust ethical frameworks, transparency in AI development, and policies that ensure benefits are shared broadly."),
            (2, voice_2, "Debater 2", "On that, we actually agree. My concern is whether we can implement those safeguards quickly enough. The technology is advancing faster than our wisdom about how to use it responsibly."),
            (1, voice_1, "Debater 1", "Which is precisely why we need more voices in this conversation, not fewer. The future of AI should be decided by humanity as a whole, not just technologists."),
            (2, voice_2, "Debater 2", "A thoughtful conclusion. Perhaps our debate illustrates the point - we need diverse perspectives and careful deliberation as we navigate this technological transformation together.")
        ]
        
        input("Press Enter to begin the debate...")
        
        for round_num, voice, debater, statement in debate_rounds:
            self.speak_as_debater(statement, voice, debater)
            time.sleep(1.5)  # Pause between speakers
        
        print("\n🎭 DEBATE COMPLETE")
        print("=" * 50)
        print("In the full system, these would be cloned voices from real people!")
    
    def run_identity_debate(self, voice_pair: Tuple[str, str] = None):
        """Run a debate about identity and AI"""
        if not voice_pair:
            voice_pair = ("Karen", "Albert")  # Australian vs American
        
        voice_1, voice_2 = voice_pair
        
        print("\n🎭 IDENTITY & AI DEBATE")
        print("=" * 50)
        print(f"🎯 Topic: What Defines Human Identity in the Age of AI?")
        print(f"   Debater 1 ({voice_1}): Identity evolutionist")
        print(f"   Debater 2 ({voice_2}): Identity purist")
        print("=" * 50)
        
        identity_script = [
            (1, voice_1, "Debater 1", "Human identity has always evolved with our tools. From language to writing to the internet, technology shapes who we are. AI is just the next step in this journey."),
            (2, voice_2, "Debater 2", "But there's something fundamentally different about AI. When a machine can replicate our voices, our writing, even our thinking patterns, what remains uniquely human?"),
            (1, voice_1, "Debater 1", "Our consciousness, our lived experiences, our capacity for love and suffering. These can't be replicated, only simulated."),
            (2, voice_2, "Debater 2", "How do we know? And even if that's true today, what about tomorrow? Are we slowly surrendering the very essence of what makes us human?"),
            (1, voice_1, "Debater 1", "I think we're expanding it. AI allows us to explore new forms of creativity and expression. It's not replacing human identity - it's augmenting it."),
            (2, voice_2, "Debater 2", "That's a beautiful idea, but I worry about the practical reality. When AI can write poetry, compose music, and hold conversations, what value do we place on human creativity?"),
            (1, voice_1, "Debater 1", "The same value we've always placed on it - the meaning comes from the human experience behind it, not just the output."),
            (2, voice_2, "Debater 2", "Perhaps you're right. Maybe identity isn't about what we can do, but about why we do it, and the consciousness that drives our choices.")
        ]
        
        input("Press Enter to begin the identity debate...")
        
        for round_num, voice, debater, statement in identity_script:
            self.speak_as_debater(statement, voice, debater)
            time.sleep(1.5)
        
        print("\n🎭 IDENTITY DEBATE COMPLETE")
        print("=" * 50)
    
    def test_voice_pairs(self):
        """Test different voice combinations"""
        print("\n🎤 Testing Available Voice Pairs")
        print("=" * 40)
        
        test_phrase = "Hello, I'm ready to participate in this debate about artificial intelligence."
        
        for i, (voice1, voice2) in enumerate(self.voice_pairs, 1):
            print(f"\n{i}. Testing pair: {voice1} vs {voice2}")
            
            print(f"   Voice 1 ({voice1}):")
            os.system(f'say -v "{voice1}" "{test_phrase}"')
            time.sleep(0.5)
            
            print(f"   Voice 2 ({voice2}):")
            os.system(f'say -v "{voice2}" "{test_phrase}"')
            time.sleep(1)
    
    def show_available_voices(self):
        """Show available voice pairs"""
        print("\n🗣️  Available Voice Pairs for Debates:")
        print("=" * 40)
        
        for i, (voice1, voice2) in enumerate(self.voice_pairs, 1):
            print(f"{i}. {voice1} vs {voice2}")


def main():
    """Main function"""
    print("🎭 TWO-VOICE DEBATE DEMONSTRATION")
    print("=" * 50)
    print("This simulates what your voice cloning system will sound like")
    print("using different macOS voices as stand-ins for cloned voices")
    print("=" * 50)
    
    # Initialize system
    debate_system = TwoVoiceDebateSystem()
    
    # Show available options
    debate_system.show_available_voices()
    
    print("\n🎯 Available Options:")
    print("1. Run AI Ethics Debate")
    print("2. Run Identity & AI Debate")
    print("3. Test voice pairs")
    print("4. Custom debate with voice selection")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                debate_system.run_ai_debate()
            
            elif choice == "2":
                debate_system.run_identity_debate()
            
            elif choice == "3":
                debate_system.test_voice_pairs()
            
            elif choice == "4":
                print("\nAvailable voice pairs:")
                debate_system.show_available_voices()
                try:
                    pair_choice = int(input("Select voice pair (1-4): ")) - 1
                    if 0 <= pair_choice < len(debate_system.voice_pairs):
                        selected_pair = debate_system.voice_pairs[pair_choice]
                        print("\nWhich debate topic?")
                        print("1. AI Ethics")
                        print("2. Identity & AI")
                        topic_choice = input("Select topic (1-2): ").strip()
                        
                        if topic_choice == "1":
                            debate_system.run_ai_debate(selected_pair)
                        elif topic_choice == "2":
                            debate_system.run_identity_debate(selected_pair)
                        else:
                            print("Invalid topic choice")
                    else:
                        print("Invalid voice pair selection")
                except ValueError:
                    print("Please enter a valid number")
            
            elif choice == "5":
                print("👋 Goodbye!")
                break
            
            else:
                print("Please select 1-5")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()