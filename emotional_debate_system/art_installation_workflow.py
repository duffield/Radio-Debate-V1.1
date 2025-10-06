#!/usr/bin/env python3
"""
Art Installation Workflow for Voice Cloning Debate System
Complete workflow from visitor voice recording to emotional debate generation
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import warnings

import sounddevice as sd
import soundfile as sf
import numpy as np
import psutil

from m1_optimized_voice import M1OptimizedVoiceAgent

warnings.filterwarnings("ignore", category=UserWarning)


class ArtInstallationWorkflow:
    """
    Complete workflow for art installation:
    1. Record visitor voice
    2. Clone voice with Chatterbox
    3. Generate debate statements
    4. Play debate with emotional responses
    5. Clean up visitor data
    """

    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.voice_agent = None
        self.visitor_voice_path = None
        self.debate_cache = {}
        self.session_id = None
        
        # Debate statements for emotional debate
        self.debate_statements = [
            # Opening
            "Welcome to this exploration of identity and artificial intelligence.",
            "I am speaking to you with your own voice now.",
            "How does it feel to hear yourself say these words?",
            
            # Core questions
            "What defines human identity in an age of artificial minds?",
            "Can a machine truly understand the weight of human emotion?",
            "When I speak with your voice, who is really speaking?",
            "Are you still you when your voice can be replicated perfectly?",
            
            # Philosophical depth
            "I process your words but do I feel their meaning?",
            "Your voice carries the echo of every word you've ever spoken.",
            "In copying your voice, have I stolen a part of your identity?",
            "Or have I simply learned to dance with the patterns of your speech?",
            
            # Emotional responses
            "There is something haunting about hearing your own voice speak thoughts you never had.",
            "I wonder if this is how you felt the first time you heard a recording of yourself.",
            "Your voice is both you and not you, familiar yet strange.",
            
            # Closing reflection  
            "This conversation will end, but the questions linger.",
            "When you leave, I will forget your voice, but you may remember mine.",
            "What stays with us when the artificial becomes indistinguishable from the real?",
            "Thank you for sharing your voice, and through it, a piece of yourself."
        ]
        
        print("🎭 Art Installation Workflow initialized")

    def setup_session(self, visitor_name: str = None) -> str:
        """Initialize a new visitor session"""
        import uuid
        self.session_id = str(uuid.uuid4())[:8]
        
        visitor_name = visitor_name or f"visitor_{self.session_id}"
        self.visitor_voice_path = self.temp_dir / f"voice_{self.session_id}.wav"
        
        print(f"🆔 Session started: {self.session_id}")
        print(f"👤 Visitor: {visitor_name}")
        
        return self.session_id

    def record_voice_sample(self, duration: int = 15, show_instructions: bool = True) -> bool:
        """
        Record visitor's voice sample for cloning
        Returns True if successful
        """
        if show_instructions:
            self.show_recording_instructions(duration)
        
        print(f"🎤 Recording voice sample for {duration} seconds...")
        print("   Speak naturally and clearly about yourself or your thoughts.")
        
        try:
            # Record audio
            print("🔴 Recording started...")
            audio_data = sd.rec(
                int(duration * 22050),  # frames
                samplerate=22050,
                channels=1,
                dtype=np.float32
            )
            
            # Simple countdown
            for i in range(duration, 0, -1):
                print(f"   {i}s remaining...", end='\r')
                time.sleep(1)
            
            sd.wait()  # Wait for recording to complete
            print("\n✅ Recording complete!")
            
            # Save the audio
            sf.write(self.visitor_voice_path, audio_data, 22050)
            print(f"💾 Voice sample saved: {self.visitor_voice_path}")
            
            # Verify the file
            if os.path.exists(self.visitor_voice_path):
                file_size = os.path.getsize(self.visitor_voice_path)
                print(f"   File size: {file_size / 1024:.1f} KB")
                return True
            else:
                print("❌ Failed to save voice sample")
                return False
                
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return False

    def show_recording_instructions(self, duration: int):
        """Show instructions to the visitor before recording"""
        instructions = [
            "🎭 VOICE RECORDING INSTRUCTIONS",
            "="*50,
            "",
            f"You will have {duration} seconds to speak.",
            "The system needs to learn your voice patterns.",
            "",
            "Tips for best results:",
            "• Speak clearly and naturally",
            "• Talk about yourself, your thoughts, or experiences", 
            "• Use varied sentence lengths and emotions",
            "• Don't worry about what to say - just be yourself",
            "",
            "Example topics:",
            "• Describe your day or week",
            "• Share a memory or experience",
            "• Talk about your interests or hobbies",
            "• Express your thoughts on technology or AI",
            "",
            "Press Enter when ready to begin recording..."
        ]
        
        for line in instructions:
            print(line)
        
        input()  # Wait for user to press Enter

    def initialize_voice_cloning(self) -> bool:
        """Initialize the voice cloning system with recorded sample"""
        if not self.visitor_voice_path or not os.path.exists(self.visitor_voice_path):
            print("❌ No voice sample available for cloning")
            return False
        
        print("🤖 Initializing voice cloning system...")
        
        try:
            # Initialize the M1 optimized voice agent
            self.voice_agent = M1OptimizedVoiceAgent(str(self.visitor_voice_path))
            
            if self.voice_agent.initialize_model():
                print("✅ Voice cloning system ready!")
                return True
            else:
                print("❌ Failed to initialize voice cloning")
                return False
                
        except Exception as e:
            print(f"❌ Voice cloning initialization failed: {e}")
            return False

    def prepare_debate(self, show_progress: bool = True) -> bool:
        """Pre-generate all debate audio for instant playback"""
        if not self.voice_agent:
            print("❌ Voice agent not initialized")
            return False
        
        if show_progress:
            print("🎯 Preparing personalized debate...")
            print("   This may take 30-60 seconds...")
            print("   (Visitors typically expect this preparation time)")
        
        try:
            # Pre-generate all debate statements
            self.debate_cache = self.voice_agent.pre_generate_statements(
                self.debate_statements,
                str(self.visitor_voice_path)
            )
            
            if len(self.debate_cache) > 0:
                print(f"✅ Debate prepared! {len(self.debate_cache)} statements ready")
                return True
            else:
                print("❌ No statements were successfully generated")
                return False
                
        except Exception as e:
            print(f"❌ Debate preparation failed: {e}")
            return False

    def run_debate(self, pause_between_statements: float = 2.0) -> bool:
        """Execute the full debate with pre-generated audio"""
        if not self.debate_cache:
            print("❌ Debate not prepared. Call prepare_debate() first")
            return False
        
        print("\n" + "🎭" * 30)
        print("  EMOTIONAL DEBATE BEGINS")
        print("🎭" * 30)
        print()
        
        try:
            for i, statement in enumerate(self.debate_statements, 1):
                print(f"[{i:02d}/{len(self.debate_statements):02d}] 🗣️  \"{statement}\"")
                
                # Play pre-generated audio instantly
                success = self.voice_agent.play_cached_statement(statement)
                
                if not success:
                    # Fallback: generate in real-time if not cached
                    print("   ⚠️  Generating in real-time...")
                    try:
                        self.voice_agent.speak(statement, wait=True)
                    except Exception as e:
                        print(f"   ❌ Failed to generate: {e}")
                        continue
                
                # Pause between statements for dramatic effect
                if i < len(self.debate_statements):
                    time.sleep(pause_between_statements)
            
            print("\n" + "🎭" * 30)
            print("  EMOTIONAL DEBATE COMPLETE")
            print("🎭" * 30)
            print()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Debate interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Debate execution failed: {e}")
            return False

    def cleanup_session(self, keep_analytics: bool = False) -> None:
        """Clean up visitor data and temporary files"""
        print("🧹 Cleaning up session data...")
        
        try:
            # Remove voice sample file
            if self.visitor_voice_path and os.path.exists(self.visitor_voice_path):
                os.remove(self.visitor_voice_path)
                print(f"   🗑️  Removed voice sample: {self.visitor_voice_path.name}")
            
            # Clear cached audio from memory
            if self.voice_agent:
                self.voice_agent.cleanup()
                print("   💾 Cleared audio cache")
            
            # Performance summary (optional analytics)
            if keep_analytics and self.voice_agent:
                summary = self.voice_agent.get_performance_summary()
                print(f"   📊 Session analytics:")
                print(f"      Generations: {summary.get('total_generations', 0)}")
                print(f"      Avg time: {summary.get('average_time', 0):.3f}s")
            
            print("✅ Cleanup complete - visitor data removed")
            
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

    def run_full_workflow(self, visitor_name: str = None, recording_duration: int = 15) -> bool:
        """
        Execute the complete installation workflow:
        Record → Clone → Prepare → Debate → Cleanup
        """
        print("🚀 Starting Art Installation Workflow")
        print("="*50)
        
        try:
            # Step 1: Setup session
            session_id = self.setup_session(visitor_name)
            
            # Step 2: Record voice
            print(f"\n📍 Step 1: Voice Recording")
            if not self.record_voice_sample(recording_duration):
                print("❌ Voice recording failed")
                return False
            
            # Step 3: Initialize voice cloning
            print(f"\n📍 Step 2: Voice Cloning Setup")
            if not self.initialize_voice_cloning():
                print("❌ Voice cloning setup failed")
                return False
            
            # Step 4: Prepare debate
            print(f"\n📍 Step 3: Debate Preparation")
            if not self.prepare_debate():
                print("❌ Debate preparation failed")
                return False
            
            # Step 5: Run the debate
            print(f"\n📍 Step 4: Emotional Debate")
            print("   The installation will now begin...")
            input("   Press Enter to start the debate...")
            
            if not self.run_debate():
                print("❌ Debate execution failed")
                return False
            
            # Step 6: Cleanup
            print(f"\n📍 Step 5: Cleanup")
            self.cleanup_session(keep_analytics=True)
            
            print("\n🎉 Installation workflow completed successfully!")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Workflow interrupted")
            self.cleanup_session()
            return False
        except Exception as e:
            print(f"\n❌ Workflow failed: {e}")
            self.cleanup_session()
            return False


def main():
    """Main entry point for art installation"""
    print("🎭 EMOTIONAL DEBATE INSTALLATION")
    print("="*50)
    print("An exploration of identity and artificial intelligence")
    print("through voice cloning and emotional dialogue")
    print("="*50)
    
    try:
        # Create workflow instance
        workflow = ArtInstallationWorkflow()
        
        # Get visitor information (optional)
        print("\nWelcome to the installation!")
        visitor_name = input("What would you like to be called? (optional): ").strip()
        if not visitor_name:
            visitor_name = None
        
        # Run the complete workflow
        success = workflow.run_full_workflow(
            visitor_name=visitor_name,
            recording_duration=15  # 15 second voice sample
        )
        
        if success:
            print("\n✨ Thank you for participating in this exploration")
            print("   of voice, identity, and artificial intelligence.")
        else:
            print("\n⚠️  The installation encountered some issues.")
            print("   Please try again or contact the artist for assistance.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        print("Please contact the artist for technical support.")


if __name__ == "__main__":
    # Check basic requirements
    try:
        import torch
        if not torch.backends.mps.is_available():
            print("⚠️  MPS not available. Performance may be reduced.")
    except ImportError:
        print("❌ PyTorch not found. Please run setup first:")
        print("   ./setup_m1_chatterbox.sh")
        sys.exit(1)
    
    main()