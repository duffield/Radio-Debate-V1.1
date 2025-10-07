#!/usr/bin/env python3
"""
Final attempt to solve the Hume voice cloning workflow
Based on all our discoveries
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv
from hume import HumeClient

# Load environment variables
load_dotenv()

def test_working_tts_synthesis(api_key: str):
    """Test a working TTS synthesis first."""
    print("\n🔍 Step 1: Testing working TTS synthesis...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Simplest working payload
    payload = {
        "utterances": [
            {
                "text": "Hello world, this is a test"
            }
        ]
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
    print(f"   Response: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS!")
        # Check response content type
        content_type = response.headers.get('content-type', '')
        print(f"   Content-Type: {content_type}")
        
        if 'json' in content_type:
            data = response.json()
            print(f"   Response structure: {json.dumps(data, indent=2)[:500]}")
            return data
        else:
            print("   Response is audio data")
            print(f"   Response size: {len(response.content)} bytes")
            # Save for analysis
            with open("test_synthesis.mp3", "wb") as f:
                f.write(response.content)
            print("   Saved as test_synthesis.mp3")
    else:
        print(f"   Error: {response.text[:300]}")
    
    return None

def test_tts_with_voice_id(api_key: str):
    """Test TTS with proper voice structure."""
    print("\n🔍 Step 2: Testing TTS with voice ID...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Use proper voice structure based on error messages
    payload = {
        "utterances": [
            {
                "text": "Hello world, this is a test"
            }
        ],
        "voice": {
            "id": "06646694-ba2a-4bca-ae3c-71d79c6b04a3"  # Known Hume voice
        }
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
    print(f"   Response: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS with voice ID!")
    else:
        print(f"   Error: {response.text[:300]}")

def test_tts_with_generation_context(api_key: str, generation_id: str = None):
    """Test using a generation_id as context."""
    print("\n🔍 Step 3: Testing TTS with generation context...")
    
    if not generation_id:
        generation_id = "00000000-0000-0000-0000-000000000000"  # Dummy for testing
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "utterances": [
            {
                "text": "Test with generation context"
            }
        ],
        "context": {
            "generation_id": generation_id
        }
    }
    
    print(f"   Using generation_id: {generation_id}")
    
    response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
    print(f"   Response: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS with generation context!")
        return response
    else:
        print(f"   Error: {response.text[:300]}")
    
    return None

def test_create_generation_with_samples(api_key: str):
    """Test creating a generation with voice samples."""
    print("\n🔍 Step 4: Testing generation with voice samples...")
    
    # Load audio file
    with open("voice_recording.wav", "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Try to synthesize with context that includes utterances (voice samples)
    payload = {
        "utterances": [
            {
                "text": "Clone my voice and say this text"
            }
        ],
        "context": {
            "utterances": [
                {
                    "text": "",  # Empty text, just voice sample
                    "audio": audio_base64
                }
            ]
        },
        "num_generations": 1  # Request a new voice generation
    }
    
    print("   Attempting synthesis with voice sample context...")
    
    response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
    print(f"   Response: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS with voice samples!")
        # Check if we get a generation_id in response
        content_type = response.headers.get('content-type', '')
        if 'json' in content_type:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}")
            
            # Look for generation_id
            if 'generation_id' in data:
                print(f"   🎉 Found generation_id: {data['generation_id']}")
                return data['generation_id']
    else:
        print(f"   Error: {response.text[:500]}")
    
    return None

def test_sdk_synthesis_minimal(api_key: str):
    """Test minimal SDK synthesis to understand response."""
    print("\n🔍 Step 5: Testing SDK synthesis (minimal)...")
    
    client = HumeClient(api_key=api_key)
    
    try:
        from hume.tts.types import PostedUtterance
        
        # Minimal utterance
        utterance = PostedUtterance(text="Test synthesis")
        
        print("   Attempting synthesize_json...")
        response = client.tts.synthesize_json(utterances=[utterance])
        
        print(f"   Response type: {type(response)}")
        
        # Explore response
        if hasattr(response, '__dict__'):
            attrs = response.__dict__
            print(f"   Response attributes: {list(attrs.keys())}")
            
            # Print each attribute
            for key, value in attrs.items():
                if not key.startswith('_'):
                    if isinstance(value, (str, int, float, bool, type(None))):
                        print(f"     {key}: {value}")
                    elif isinstance(value, bytes):
                        print(f"     {key}: <bytes, length={len(value)}>")
                    elif isinstance(value, list):
                        print(f"     {key}: <list, length={len(value)}>")
                    else:
                        print(f"     {key}: <{type(value).__name__}>")
                        
                    # Special check for generation_id
                    if 'generation' in key.lower() or 'id' in key.lower():
                        print(f"       🔍 Potential ID field: {key} = {value}")
        
        return response
        
    except Exception as e:
        print(f"   Error: {e}")
        return None

def final_solution_attempt(api_key: str):
    """Final attempt using all learnings."""
    print("\n🎙️ FINAL SOLUTION ATTEMPT")
    print("=" * 50)
    
    # Step 1: Do a normal synthesis to understand the response
    response = test_sdk_synthesis_minimal(api_key)
    
    if response and hasattr(response, 'generation_id'):
        generation_id = response.generation_id
        print(f"\n✅ Got generation_id from synthesis: {generation_id}")
        
        # Step 2: Try to create a voice with this generation_id
        client = HumeClient(api_key=api_key)
        try:
            print("\nCreating voice with generation_id...")
            voice = client.tts.voices.create(
                generation_id=str(generation_id),
                name="Cloned Voice Test"
            )
            print(f"🎉 SUCCESS! Voice created with ID: {voice.id}")
            return voice.id
        except Exception as e:
            print(f"Error creating voice: {e}")
    
    return None

def main():
    """Main test function."""
    print("🎙️ Hume AI Voice Cloning Solution Test")
    print("=" * 50)
    
    # Get API key
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found in environment")
        return
    
    # Check if audio file exists
    if not os.path.exists("voice_recording.wav"):
        print("❌ voice_recording.wav not found")
        return
    
    print("✅ Found voice_recording.wav")
    
    # Run tests in sequence
    test_working_tts_synthesis(api_key)
    test_tts_with_voice_id(api_key)
    test_tts_with_generation_context(api_key)
    
    generation_id = test_create_generation_with_samples(api_key)
    
    if generation_id:
        print(f"\n🎉 Got generation_id: {generation_id}")
        # Try to create voice with it
        client = HumeClient(api_key=api_key)
        try:
            voice = client.tts.voices.create(
                generation_id=str(generation_id),
                name="My Cloned Voice"
            )
            print(f"🎉 Voice created successfully! ID: {voice.id}")
        except Exception as e:
            print(f"Error creating voice: {e}")
    
    # Final solution attempt
    voice_id = final_solution_attempt(api_key)
    
    if voice_id:
        print(f"\n🎉🎉🎉 COMPLETE SUCCESS!")
        print(f"Voice ID: {voice_id}")
        print("You can now use this voice in your Empathic Voice configs!")
    
    print("\n" + "=" * 50)
    print("🔍 Solution test complete.")

if __name__ == "__main__":
    main()