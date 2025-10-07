#!/usr/bin/env python3
"""
Debug script to understand how Hume actually clones voices
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv
from hume import HumeClient

load_dotenv()

def test_context_with_audio(api_key: str):
    """Test if we can provide audio context for voice cloning."""
    print("\n🔍 Testing context with audio samples...")
    
    # Load audio
    with open("voice_recording.wav", "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test different context structures
    test_contexts = [
        {
            # Context with generation_id (placeholder)
            "utterances": [{"text": "Test"}],
            "context": {
                "generation_id": "placeholder"
            }
        },
        {
            # Context with utterances including audio
            "utterances": [{"text": "Test"}],
            "context": {
                "utterances": [
                    {
                        "text": "",
                        "audio": audio_base64
                    }
                ]
            }
        },
        {
            # Just utterances with audio directly
            "utterances": [
                {
                    "text": "Test",
                    "audio": audio_base64
                }
            ]
        }
    ]
    
    for i, payload in enumerate(test_contexts):
        print(f"\n📤 Test {i+1}: {list(payload.keys())}")
        response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            error = response.text[:300]
            print(f"   Error: {error}")
            # Look for clues in error messages
            if "generation_id" in error:
                print("   💡 Needs valid generation_id")
            if "utterances" in error and "audio" in error:
                print("   💡 Audio might need different format or field name")

def check_voice_details(api_key: str, voice_id: str):
    """Check details of the created voice."""
    print(f"\n🔍 Checking voice details for: {voice_id}")
    
    client = HumeClient(api_key=api_key)
    
    # List all voices to see if ours is custom
    try:
        voices = client.tts.voices.list(provider="HUME_AI")
        
        found = False
        for voice in voices:
            if voice.id == voice_id:
                found = True
                print(f"   Found voice: {voice.name}")
                print(f"   Tags: {voice.tags if hasattr(voice, 'tags') else 'No tags'}")
                print(f"   Provider: {voice.provider}")
                break
        
        if not found:
            print("   ⚠️  Voice not found in list - might be truly custom")
            
    except Exception as e:
        print(f"   Error: {e}")

def test_synthesis_with_num_generations(api_key: str):
    """Test if num_generations actually uses voice samples."""
    print("\n🔍 Testing if synthesis uses voice samples from audio...")
    
    # Load audio
    with open("voice_recording.wav", "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    client = HumeClient(api_key=api_key)
    
    # Try SDK with different approaches
    from hume.tts.types import PostedUtterance, PostedContextWithUtterances
    
    try:
        # Attempt 1: Context with utterances containing audio
        context = PostedContextWithUtterances(
            utterances=[
                {
                    "text": "",
                    "audio": audio_base64
                }
            ]
        )
        
        utterance = PostedUtterance(text="Testing voice clone")
        
        print("   Attempting synthesis with audio context...")
        response = client.tts.synthesize_json(
            utterances=[utterance],
            context=context,
            num_generations=1
        )
        
        if hasattr(response, 'generations') and len(response.generations) > 0:
            gen = response.generations[0]
            print(f"   Got generation_id: {gen.generation_id}")
            return gen.generation_id
            
    except Exception as e:
        print(f"   Error: {e}")
        
    return None

def check_api_docs(api_key: str):
    """Check if there's documentation about voice cloning."""
    print("\n🔍 Looking for voice cloning documentation...")
    
    # Check different potential documentation endpoints
    headers = {"X-Hume-Api-Key": api_key}
    
    endpoints = [
        "https://api.hume.ai/docs",
        "https://api.hume.ai/v0/docs",
        "https://api.hume.ai/help",
        "https://api.hume.ai/v0/voice/clone",
        "https://api.hume.ai/v0/tts/clone",
    ]
    
    for endpoint in endpoints:
        response = requests.get(endpoint, headers=headers)
        if response.status_code != 404:
            print(f"   Found endpoint: {endpoint} (status: {response.status_code})")

def main():
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found")
        return
    
    print("🔍 DEBUGGING HUME VOICE CLONING")
    print("=" * 50)
    
    # Check the voice we created
    voice_id = "738e5f2b-62a5-4477-b02c-977ec465e295"
    check_voice_details(api_key, voice_id)
    
    # Test context approaches
    test_context_with_audio(api_key)
    
    # Test synthesis approaches
    generation_id = test_synthesis_with_num_generations(api_key)
    if generation_id:
        print(f"\n💡 Got generation_id: {generation_id}")
        print("   But this might not use the audio samples...")
    
    # Check for documentation
    check_api_docs(api_key)
    
    print("\n" + "=" * 50)
    print("🤔 CONCLUSION:")
    print("The Hume API may not support direct voice cloning from audio samples")
    print("through the public API. Voice cloning might require:")
    print("1. Using their web interface")
    print("2. Special API access or endpoints")
    print("3. A different service (like Hume's Voice Lab)")

if __name__ == "__main__":
    main()