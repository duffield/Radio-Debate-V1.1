#!/usr/bin/env python3
"""
Test your cloned voice by synthesizing speech
"""

import os
from dotenv import load_dotenv
from hume import HumeClient
from hume.tts.types import PostedUtterance, PostedUtteranceVoiceWithId

# Load environment variables
load_dotenv()

def test_cloned_voice(api_key: str, voice_id: str):
    """Test the cloned voice by synthesizing some text."""
    
    print("🎤 Testing Your Cloned Voice")
    print("=" * 50)
    
    client = HumeClient(api_key=api_key)
    
    # Get text to synthesize
    text = input("\nEnter text to synthesize with your cloned voice: ")
    if not text:
        text = "Hello! This is a test of my cloned voice using Hume AI. It's amazing that this is working!"
    
    print(f"\n🔊 Synthesizing: '{text}'")
    
    try:
        # Create utterance with your cloned voice
        utterance = PostedUtterance(
            text=text,
            voice=PostedUtteranceVoiceWithId(id=voice_id)
        )
        
        # Synthesize to file
        print("   Generating audio...")
        audio_bytes = client.tts.synthesize_file(
            utterances=[utterance]
        )
        
        # Save the audio
        output_file = "cloned_voice_output.mp3"
        with open(output_file, "wb") as f:
            for chunk in audio_bytes:
                f.write(chunk)
        
        print(f"   ✅ Success! Audio saved to: {output_file}")
        print(f"\n🎵 You can now play {output_file} to hear your cloned voice!")
        
        # Try to play it automatically if possible
        try:
            os.system(f"afplay {output_file}")  # macOS command to play audio
        except:
            pass
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found")
        return
    
    # Use the newly created voice ID
    voice_id = "738e5f2b-62a5-4477-b02c-977ec465e295"
    
    test_cloned_voice(api_key, voice_id)

if __name__ == "__main__":
    main()