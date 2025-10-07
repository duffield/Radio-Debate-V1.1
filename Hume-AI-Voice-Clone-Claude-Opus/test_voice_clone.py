#!/usr/bin/env python3
"""
Test script for Hume AI Voice Cloning API
Uses existing voice_recording.wav to test voice cloning without re-recording
"""

import os
import base64
import requests
from dotenv import load_dotenv
from hume import HumeClient

# Load environment variables
load_dotenv()

def load_audio_file(filename: str) -> bytes:
    """Load audio file as bytes."""
    with open(filename, 'rb') as f:
        return f.read()

def test_voice_clone_direct_api(api_key: str, audio_data: bytes, voice_name: str):
    """Test voice cloning using direct API calls."""
    print(f"\n🔄 Testing direct API voice clone creation...")
    
    # Encode audio to base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Test different API endpoints and structures
    test_endpoints = [
        "https://api.hume.ai/v0/voice/custom_voices",
        "https://api.hume.ai/v0/tts/voices", 
        "https://api.hume.ai/v0/tts/custom_voices",
    ]
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test payload structures
    test_payloads = [
        # Original structure
        {
            "name": voice_name,
            "base_voice": "ITO",
            "parameters": {
                "gender": -5,
                "huskiness": -5,
                "nasality": -8,
                "pitch": -5
            },
            "samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        },
        # TTS structure with provider
        {
            "provider": "HUME_AI",
            "name": voice_name,
            "samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        },
        # Simplified structure
        {
            "name": voice_name,
            "samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        }
    ]
    
    for i, endpoint in enumerate(test_endpoints):
        for j, payload in enumerate(test_payloads):
            print(f"\n📤 Testing endpoint {i+1}.{j+1}: {endpoint}")
            print(f"   Payload structure: {list(payload.keys())}")
            
            response = requests.post(endpoint, headers=headers, json=payload)
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS! Voice ID: {result.get('id', 'No ID returned')}")
                print(f"   Full response: {result}")
                return result.get('id')
            else:
                print(f"   ❌ Error: {response.text[:200]}...")
    
    return None

def test_voice_clone_sdk(api_key: str, audio_data: bytes, voice_name: str):
    """Test voice cloning using Hume SDK."""
    print(f"\n🔄 Testing SDK voice clone creation...")
    
    try:
        client = HumeClient(api_key=api_key)
        
        # First, let's see what's available
        print("Available TTS methods:", [attr for attr in dir(client.tts.voices) if not attr.startswith('_')])
        
        # Try to list existing voices first
        try:
            # This might need a provider parameter
            voices = client.tts.voices.list()
            print(f"Existing voices: {voices}")
        except Exception as e:
            print(f"Could not list voices: {e}")
            
            # Try with provider
            try:
                voices = client.tts.voices.list(provider="HUME_AI")  # This might not work but let's try
                print(f"Existing voices with provider: {voices}")
            except Exception as e2:
                print(f"Could not list voices with provider: {e2}")
        
        # The SDK create method needs a generation_id, which suggests a different workflow
        # This might not work directly, but let's see what error we get
        print("SDK create method requires generation_id - this might be a multi-step process")
        
    except Exception as e:
        print(f"SDK error: {e}")
    
    return None

def main():
    """Main test function."""
    print("🎙️ Hume AI Voice Cloning API Test")
    print("=" * 50)
    
    # Get API key
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found in environment")
        return
    
    # Load existing audio recording
    try:
        audio_data = load_audio_file("voice_recording.wav")
        print(f"✅ Loaded voice_recording.wav ({len(audio_data)} bytes)")
    except FileNotFoundError:
        print("❌ voice_recording.wav not found. Run main.py first to record audio.")
        return
    
    voice_name = "Test-SDK-01"
    
    # Test direct API approach
    voice_id_direct = test_voice_clone_direct_api(api_key, audio_data, voice_name)
    
    # Test SDK approach  
    voice_id_sdk = test_voice_clone_sdk(api_key, audio_data, voice_name)
    
    if voice_id_direct:
        print(f"\n✅ SUCCESS with direct API! Voice ID: {voice_id_direct}")
    elif voice_id_sdk:
        print(f"\n✅ SUCCESS with SDK! Voice ID: {voice_id_sdk}")
    else:
        print(f"\n❌ No successful voice clone creation method found")
        print("🔍 This suggests the API has changed significantly from the original implementation")

if __name__ == "__main__":
    main()