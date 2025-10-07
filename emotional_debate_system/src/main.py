#!/usr/bin/env python3
"""
Emotional AI Debate System
Main entry point
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
# Add parent directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import config
from llm.ollama_provider import OllamaLLM
from emotion.detector import EmotionDetector
from tts.coqui_provider import CoquiTTS
from tts.macos_provider import MacOSTTS
from tts.chatterbox_provider import ChatterboxTTS
from streaming.osc_streamer import OSCStreamer

class DebateSystem:
    """Main debate orchestrator"""
    
    def __init__(self):
        print("🦎 Initializing Emotional AI Debate System...")
        print("="*60)
        
        # Initialize components
        print("\n🤖 Loading LLM...")
        self.llm = OllamaLLM(
            model=config.llm.model,
            host=config.llm.host
        )
        
        # Check if Ollama is available
        if not self.llm.is_available():
            print("❌ Ollama is not running!")
            print("   Start it with: ollama serve")
            sys.exit(1)
        
        print("\n🧠 Loading emotion detector...")
        self.emotion_detector = EmotionDetector(
            model=config.emotion.model,
            device=config.emotion.device
        )
        
        print("\n🔊 Loading TTS...")
        # FORCE Chatterbox TTS with voice cloning - NO fallbacks
        print("  Using Chatterbox TTS with voice cloning")
        self.tts = ChatterboxTTS()
        if not self.tts.is_available():
            print("❌ Chatterbox TTS is required but not available!")
            print("   Install with: pip install chatterbox")
            sys.exit(1)
        
        print("\n📡 Initializing OSC streaming...")
        self.osc = OSCStreamer(
            ip=config.osc.ip,
            port=config.osc.port,
            fps=config.osc.fps
        )
        
        # Debate state
        self.debate_history = []
        
        print("\n" + "="*60)
        print("✅ System ready!\n")
    
    def run_debate_round(self, topic: str, rounds: int = 5):
        """Run a complete debate"""
        
        print(f"🎭 Starting debate on:\n   '{topic}'\n")
        print("="*60)
        
        agents = [
            ("Truth Seeker", "worried"),
            ("Skeptic", "skeptical")
        ]
        
        last_response = f"Let's discuss: {topic}"
        
        for round_num in range(rounds):
            print(f"\n📊 Round {round_num + 1}/{rounds}")
            print("-"*60)
            
            for agent_name, character in agents:
                # Generate response
                prompt = f"Respond to: {last_response}"
                
                print(f"\n💭 {agent_name} is thinking...")
                
                try:
                    response = self.llm.generate_with_emotion(prompt, character)
                    
                    # Enrich with emotion detection
                    response = self.emotion_detector.enrich_emotions(
                        response, 
                        threshold=config.emotion.threshold
                    )
                    
                    # Display
                    print(f"\n[{agent_name}]: {response.text}")
                    
                    # Show top 3 emotions
                    emotion_str = ', '.join([
                        f'{e.name}({e.intensity:.2f})' 
                        for e in response.emotions[:3]
                    ])
                    print(f"  Emotions: {emotion_str}")
                    print(f"  Valence: {response.valence:+.2f} | Arousal: {response.arousal:.2f}")
                    
                    # Stream to TouchDesigner
                    agent_id = agent_name.lower().replace(" ", "_")
                    self.osc.stream_debate_response(response, agent_id)
                    
                    # Synthesize speech (optional)
                    if config.tts.save_audio:
                        print(f"  🎤 Generating speech...")
                        # Pass character info for voice selection
                        audio_path = self.tts.synthesize(response, character=character)
                        print(f"  💾 Saved: {audio_path.name}")
                    
                    # Update for next round
                    last_response = response.text
                    self.debate_history.append({
                        'agent': agent_name,
                        'round': round_num + 1,
                        'response': response.model_dump()
                    })
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    if config.debug:
                        import traceback
                        traceback.print_exc()
                
                time.sleep(1)  # Pause between speakers
            
            print("\n" + "="*60)
        
        print("\n🏁 Debate complete!")
        print(f"📝 Total exchanges: {len(self.debate_history)}")
        return self.debate_history

def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Emotional AI Debate System")
    parser.add_argument('--topic', type=str, 
                       default="Should we worry about shapeshifting lizard people controlling world governments?",
                       help="Debate topic")
    parser.add_argument('--rounds', type=int, default=3,
                       help="Number of debate rounds")
    parser.add_argument('--no-audio', action='store_true',
                       help="Disable audio synthesis")
    parser.add_argument('--audio', action='store_true',
                       help="Enable audio synthesis")
    
    args = parser.parse_args()
    
    # Override config if needed
    if args.no_audio:
        config.tts.save_audio = False
    elif args.audio:
        config.tts.save_audio = True
    
    try:
        system = DebateSystem()
        system.run_debate_round(topic=args.topic, rounds=args.rounds)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Debate interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
