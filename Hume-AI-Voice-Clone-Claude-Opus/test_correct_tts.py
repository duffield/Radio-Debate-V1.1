#!/usr/bin/env python3
"""
Test the correct TTS synthesis format to get a generation_id
Based on findings, we need to use utterances parameter
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

def test_tts_synthesis_correct_format(api_key: str):
    """Test TTS synthesis with correct utterances format."""
    print("\n🔍 Testing TTS synthesis with correct format...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test different utterance formats
    test_payloads = [
        {
            "utterances": [
                {
                    "text": "Hello world, this is a test",
                    "provider": "HUME_AI"
                }
            ]
        },
        {
            "utterances": [
                {
                    "text": "Hello world, this is a test",
                    "voice_id": "06646694-ba2a-4bca-ae3c-71d79c6b04a3"  # Using a known voice ID from earlier
                }
            ]
        },
        {
            "utterances": [
                {
                    "text": "Hello world, this is a test"
                }
            ],
            "version": "2"
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f"\n📤 Testing payload {i+1}")
        print(f"   Payload: {json.dumps(payload, indent=2)[:200]}...")
        
        response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
        print(f"   Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ SUCCESS!")
            try:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                # Look for generation_id or any ID
                for key in ['id', 'generation_id', 'record_id', 'tts_id']:
                    if key in data:
                        print(f"   Found {key}: {data[key]}")
                        return data[key]
                        
                # Print full response to understand structure
                print(f"   Full response: {json.dumps(data, indent=2)[:500]}...")
                
            except Exception as e:
                print(f"   Error parsing response: {e}")
                # It might be audio data
                print(f"   Response preview: {response.content[:100]}")
        else:
            print(f"   Error: {response.text[:300]}...")

def test_tts_synthesis_with_sdk(api_key: str):
    """Test TTS synthesis using SDK to get generation_id."""
    print("\n🔍 Testing TTS synthesis with SDK...")
    
    client = HumeClient(api_key=api_key)
    
    try:
        # Create proper PostedUtterance
        utterance = PostedUtterance(
            text="Hello world, this is a test synthesis",
            voice_id="06646694-ba2a-4bca-ae3c-71d79c6b04a3"  # Using a known voice
        )
        
        print("Attempting synthesize_json with PostedUtterance...")
        response = client.tts.synthesize_json(
            utterances=[utterance]
        )
        
        print(f"Response type: {type(response)}")
        
        # Check response attributes
        if hasattr(response, '__dict__'):
            print(f"Response attributes: {list(response.__dict__.keys())}")
            
            # Look for ID fields
            for attr in ['id', 'generation_id', 'record_id', 'tts_id']:
                if hasattr(response, attr):
                    value = getattr(response, attr)
                    print(f"Found {attr}: {value}")
                    return value
                    
            # Print all attributes
            for key, value in response.__dict__.items():
                if not key.startswith('_'):
                    print(f"  {key}: {str(value)[:100]}")
                    
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

def test_synthesis_then_voice_creation(api_key: str):
    """Test if we can create a voice after synthesis."""
    print("\n🔍 Testing synthesis followed by voice creation...")
    
    client = HumeClient(api_key=api_key)
    
    try:
        # Step 1: Synthesize with a test utterance
        utterance = PostedUtterance(
            text="This is a test to generate a voice ID",
            provider="HUME_AI"
        )
        
        print("Step 1: Synthesizing...")
        response = client.tts.synthesize_json(
            utterances=[utterance],
            num_generations=1  # Try to generate a new voice
        )
        
        print(f"Synthesis response type: {type(response)}")
        
        # Check if response has a generation_id
        if hasattr(response, 'generation_id'):
            generation_id = response.generation_id
            print(f"✅ Got generation_id: {generation_id}")
            
            # Step 2: Try to create a voice with this generation_id
            print("\nStep 2: Creating voice with generation_id...")
            voice = client.tts.voices.create(
                generation_id=str(generation_id),
                name="Test Voice from Generation"
            )
            
            print(f"✅ Voice created! ID: {voice.id}")
            return voice.id
            
    except Exception as e:
        print(f"Error: {e}")

def test_synthesis_with_custom_voice_samples(api_key: str):
    """Test if synthesis can accept voice samples for cloning."""
    print("\n🔍 Testing synthesis with voice samples...")
    
    # Load audio file
    with open("voice_recording.wav", "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Try different ways to include voice samples
    test_payloads = [
        {
            "utterances": [
                {
                    "text": "Clone my voice and say this",
                    "voice": {
                        "samples": [{
                            "data": audio_base64,
                            "mime_type": "audio/wav"
                        }]
                    }
                }
            ]
        },
        {
            "utterances": [
                {
                    "text": "Clone my voice and say this"
                }
            ],
            "context": {
                "samples": [{
                    "data": audio_base64,
                    "mime_type": "audio/wav"
                }]
            }
        },
        {
            "utterances": [
                {
                    "text": "Clone my voice and say this"
                }
            ],
            "num_generations": 1,
            "voice_samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f"\n📤 Testing payload {i+1} with voice samples")
        
        response = requests.post("https://api.hume.ai/v0/tts", headers=headers, json=payload)
        print(f"   Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ SUCCESS with voice samples!")
            try:
                data = response.json()
                print(f"   Response structure: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for any ID that we can use
                for key in data:
                    if 'id' in key.lower():
                        print(f"   Found {key}: {data[key]}")
                        
            except:
                print("   Response is binary (audio data)")
        else:
            print(f"   Error: {response.text[:200]}...")

def main():
    """Main test function."""
    print("🎙️ Hume AI Correct TTS Format Test")
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
    
    # Run tests
    generation_id = test_tts_synthesis_correct_format(api_key)
    
    if not generation_id:
        generation_id = test_tts_synthesis_with_sdk(api_key)
    
    if not generation_id:
        test_synthesis_then_voice_creation(api_key)
    
    test_synthesis_with_custom_voice_samples(api_key)
    
    print("\n" + "=" * 50)
    print("🔍 TTS format test complete.")

if __name__ == "__main__":
    main()