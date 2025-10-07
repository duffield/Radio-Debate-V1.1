#!/usr/bin/env python3
"""
Test script to find the voice generation/upload endpoint for Hume AI
This should give us a generation_id that we can use to create the voice
"""

import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_audio_file(filename: str) -> bytes:
    """Load audio file as bytes."""
    with open(filename, 'rb') as f:
        return f.read()

def test_generation_endpoints(api_key: str, audio_data: bytes, voice_name: str):
    """Test different endpoints that might handle voice generation/upload."""
    print(f"\n🔄 Testing voice generation/upload endpoints...")
    
    # Encode audio to base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test potential generation endpoints
    generation_endpoints = [
        "https://api.hume.ai/v0/tts/generations",
        "https://api.hume.ai/v0/tts/voice_generations", 
        "https://api.hume.ai/v0/tts/uploads",
        "https://api.hume.ai/v0/tts/samples",
        "https://api.hume.ai/v0/voice/generations",
        "https://api.hume.ai/v0/voice/uploads",
    ]
    
    # Test different payload structures for generation
    generation_payloads = [
        # Basic upload structure
        {
            "name": voice_name,
            "samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        },
        # With provider
        {
            "provider": "HUME_AI",
            "name": voice_name,
            "samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        },
        # Just the sample data
        {
            "data": audio_base64,
            "mime_type": "audio/wav",
            "name": voice_name
        },
        # File-like structure
        {
            "file": {
                "data": audio_base64,
                "filename": f"{voice_name}.wav",
                "content_type": "audio/wav"
            }
        }
    ]
    
    for i, endpoint in enumerate(generation_endpoints):
        for j, payload in enumerate(generation_payloads):
            print(f"\n📤 Testing generation endpoint {i+1}.{j+1}: {endpoint}")
            print(f"   Payload keys: {list(payload.keys())}")
            
            response = requests.post(endpoint, headers=headers, json=payload)
            print(f"   Response: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:  # Success codes
                result = response.json()
                generation_id = result.get('id') or result.get('generation_id') or result.get('upload_id')
                print(f"   ✅ SUCCESS! Generation ID: {generation_id}")
                print(f"   Full response: {result}")
                return generation_id, endpoint, payload
            elif response.status_code == 422:
                # Validation error - still the right endpoint potentially
                print(f"   ⚠️  Validation error (right endpoint?): {response.text[:200]}...")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
    
    return None, None, None

def test_voice_creation_with_generation_id(api_key: str, generation_id: str, voice_name: str):
    """Test creating a voice with a generation_id."""
    print(f"\n🔄 Testing voice creation with generation_id: {generation_id}")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "generation_id": generation_id,
        "name": voice_name
    }
    
    response = requests.post("https://api.hume.ai/v0/tts/voices", headers=headers, json=payload)
    print(f"Voice creation response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        voice_id = result.get('id')
        print(f"✅ Voice created successfully! Voice ID: {voice_id}")
        return voice_id
    else:
        print(f"❌ Voice creation failed: {response.text}")
        return None

def main():
    """Main test function."""
    print("🎙️ Hume AI Voice Generation/Upload Test")
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
    
    voice_name = "Test-Generation-01"
    
    # Step 1: Find the generation/upload endpoint
    generation_id, successful_endpoint, successful_payload = test_generation_endpoints(api_key, audio_data, voice_name)
    
    if generation_id:
        print(f"\n✅ Found working generation endpoint: {successful_endpoint}")
        print(f"✅ Generation ID obtained: {generation_id}")
        
        # Step 2: Try to create voice with generation_id
        voice_id = test_voice_creation_with_generation_id(api_key, generation_id, voice_name)
        
        if voice_id:
            print(f"\n🎉 COMPLETE SUCCESS! Voice cloned with ID: {voice_id}")
            print(f"You can now use this voice_id in your Empathic Voice configs!")
        else:
            print(f"\n⚠️  Generation worked but voice creation failed")
    else:
        print(f"\n❌ No working generation endpoint found")
        print("🔍 The API might use a different approach (file upload, etc.)")

if __name__ == "__main__":
    main()