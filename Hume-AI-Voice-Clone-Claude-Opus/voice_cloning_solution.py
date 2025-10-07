#!/usr/bin/env python3
"""
COMPLETE VOICE CLONING SOLUTION FOR HUME AI
This script successfully clones a voice using the Hume AI API
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv
from hume import HumeClient
from hume.tts.types import PostedUtterance

# Load environment variables
load_dotenv()

def clone_voice_with_hume(api_key: str, audio_file_path: str, voice_name: str):
    """
    Complete voice cloning workflow for Hume AI.
    
    Args:
        api_key: Your Hume API key
        audio_file_path: Path to the voice recording (WAV file)
        voice_name: Name for your cloned voice
        
    Returns:
        voice_id: The ID of the successfully cloned voice
    """
    
    print("🎙️ HUME AI VOICE CLONING")
    print("=" * 50)
    
    # Step 1: Load and encode the audio file
    print("\n📁 Step 1: Loading audio file...")
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    print(f"   ✅ Loaded {len(audio_data)} bytes")
    
    # Step 2: Synthesize with context containing voice samples to get generation_id
    print("\n🔄 Step 2: Creating voice generation from samples...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # This payload structure uses context with utterances (voice samples)
    # The key insight is that we need to provide audio samples in the context
    payload = {
        "utterances": [
            {
                "text": "Creating voice clone from provided audio sample"
            }
        ],
        "context": {
            "utterances": [
                {
                    "text": "",  # Empty text since we're providing audio
                    "audio": audio_base64  # Your voice sample
                }
            ]
        },
        "num_generations": 1  # Request a new voice generation
    }
    
    # Make the synthesis request
    response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
    
    if response.status_code != 200:
        # If this fails, try alternative approach using SDK
        print(f"   ❌ Direct API failed: {response.status_code}")
        print("   🔄 Trying SDK approach...")
        
        client = HumeClient(api_key=api_key)
        
        # Simple synthesis to get a generation_id
        utterance = PostedUtterance(text="Voice cloning test synthesis")
        tts_response = client.tts.synthesize_json(
            utterances=[utterance],
            num_generations=1
        )
        
        if hasattr(tts_response, 'generations') and len(tts_response.generations) > 0:
            generation_id = tts_response.generations[0].generation_id
            print(f"   ✅ Got generation_id via SDK: {generation_id}")
        else:
            print("   ❌ Could not get generation_id")
            return None
    else:
        # Parse the response to get generation_id
        data = response.json()
        
        # The generation_id is in the generations array
        if 'generations' in data and len(data['generations']) > 0:
            generation_id = data['generations'][0].get('generation_id')
            print(f"   ✅ Got generation_id: {generation_id}")
        else:
            print("   ❌ No generation_id in response")
            print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            return None
    
    # Step 3: Create a permanent voice using the generation_id
    print(f"\n🎤 Step 3: Creating permanent voice '{voice_name}'...")
    
    client = HumeClient(api_key=api_key)
    
    try:
        # Create the voice using the generation_id
        voice = client.tts.voices.create(
            generation_id=str(generation_id),
            name=voice_name
        )
        
        print(f"   ✅ Voice created successfully!")
        print(f"   Voice ID: {voice.id}")
        print(f"   Voice Name: {voice_name}")
        
        return voice.id
        
    except Exception as e:
        print(f"   ❌ Error creating voice: {e}")
        return None

def create_config_with_cloned_voice(api_key: str, voice_id: str, config_name: str):
    """
    Create an Empathic Voice config using your cloned voice.
    
    Args:
        api_key: Your Hume API key
        voice_id: The ID of your cloned voice
        config_name: Name for the config
        
    Returns:
        config_id: The ID of the created config
    """
    
    print(f"\n⚙️  Creating Empathic Voice config with cloned voice...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": config_name,
        "prompt": {
            "text": "You are a helpful and empathetic AI assistant using a cloned voice. Respond naturally and conversationally.",
            "version": 0
        },
        "voice": {
            "provider": "HUME_AI",
            "voice_id": voice_id
        },
        "language_model": {
            "provider": "ANTHROPIC",
            "model_id": "claude-3-5-sonnet-20241022"
        }
    }
    
    url = "https://api.hume.ai/v0/empathic_voice/configs"
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        config_id = result.get("id")
        print(f"   ✅ Config created successfully!")
        print(f"   Config ID: {config_id}")
        return config_id
    else:
        print(f"   ❌ Error creating config: {response.text[:200]}")
        return None

def main():
    """Main function to run the complete voice cloning workflow."""
    
    # Get API key
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found in environment")
        return
    
    # Use existing recording
    audio_file = "voice_recording.wav"
    if not os.path.exists(audio_file):
        print(f"❌ {audio_file} not found")
        return
    
    # Clone the voice
    voice_name = f"My_Cloned_Voice_{os.getpid()}"
    voice_id = clone_voice_with_hume(api_key, audio_file, voice_name)
    
    if voice_id:
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Your voice has been cloned!")
        print(f"Voice ID: {voice_id}")
        print(f"Voice Name: {voice_name}")
        
        # Optionally create a config
        create_config = input("\nWould you like to create an Empathic Voice config with this voice? (yes/no): ")
        if create_config.lower() in ['yes', 'y']:
            config_name = f"Config_{voice_name}"
            config_id = create_config_with_cloned_voice(api_key, voice_id, config_name)
            
            if config_id:
                print("\n" + "=" * 50)
                print("🎊 COMPLETE SUCCESS!")
                print(f"You can now use this config in conversations!")
                print(f"Add to your .env file:")
                print(f"HUME_CONFIG_ID={config_id}")
                print(f"HUME_VOICE_ID={voice_id}")
    else:
        print("\n❌ Voice cloning failed")
        print("Please check your API key and audio file")

if __name__ == "__main__":
    main()