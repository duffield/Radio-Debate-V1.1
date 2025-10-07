#!/usr/bin/env python3
"""
Test TTS synthesis methods to understand the generation workflow
The generation_id might come from a TTS synthesis request
"""

import os
import base64
import requests
import json
import inspect
from dotenv import load_dotenv
from hume import HumeClient

# Load environment variables
load_dotenv()

def explore_tts_synthesize_methods(api_key: str):
    """Explore TTS synthesis methods in detail."""
    print("\n🔍 Exploring TTS Synthesis Methods...")
    
    client = HumeClient(api_key=api_key)
    
    # Check synthesize_file method
    print("\n=== synthesize_file method ===")
    sig = inspect.signature(client.tts.synthesize_file)
    print(f"Signature: {sig}")
    print(f"Docstring: {client.tts.synthesize_file.__doc__[:500] if client.tts.synthesize_file.__doc__ else 'No docstring'}")
    
    print("\n=== synthesize_json method ===")
    sig = inspect.signature(client.tts.synthesize_json)
    print(f"Signature: {sig}")
    print(f"Docstring: {client.tts.synthesize_json.__doc__[:500] if client.tts.synthesize_json.__doc__ else 'No docstring'}")

def test_tts_record_endpoints(api_key: str):
    """Test TTS record endpoints based on error message clue."""
    print("\n🔍 Testing TTS record endpoints...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
    }
    
    # Based on error mentioning "tts_record", test these
    record_endpoints = [
        "https://api.hume.ai/v0/tts/records",
        "https://api.hume.ai/v0/tts/tts_records",
        "https://api.hume.ai/v0/tts_records",
        "https://api.hume.ai/v0/tts/generations",
        "https://api.hume.ai/v0/tts/synthesize",
    ]
    
    for endpoint in record_endpoints:
        print(f"\n📤 Testing GET {endpoint}")
        response = requests.get(endpoint, headers=headers)
        print(f"   Response: {response.status_code}")
        if response.status_code != 404:
            print(f"   🔍 Found something! {response.text[:200]}")
            
        # Also test POST
        print(f"\n📤 Testing POST {endpoint}")
        response = requests.post(endpoint, headers=headers, json={})
        print(f"   Response: {response.status_code}")
        if response.status_code != 404:
            print(f"   🔍 Found something! {response.text[:200]}")

def test_voice_cloning_via_tts_synthesis(api_key: str):
    """Test if we can clone a voice through TTS synthesis with audio input."""
    print("\n🔍 Testing voice cloning via TTS synthesis...")
    
    # Load the audio file
    with open("voice_recording.wav", "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Try different synthesis payloads that might generate a voice
    test_payloads = [
        {
            "text": "Test synthesis",
            "voice": {
                "samples": [{
                    "data": audio_base64,
                    "mime_type": "audio/wav"
                }]
            }
        },
        {
            "text": "Test synthesis",
            "voice_samples": [{
                "data": audio_base64,
                "mime_type": "audio/wav"
            }]
        },
        {
            "text": "Test synthesis",
            "custom_voice": {
                "samples": [{
                    "data": audio_base64,
                    "mime_type": "audio/wav"
                }],
                "name": "Test Voice"
            }
        }
    ]
    
    synthesis_endpoints = [
        "https://api.hume.ai/v0/tts/synthesize",
        "https://api.hume.ai/v0/tts/synthesize_json",
        "https://api.hume.ai/v0/tts",
    ]
    
    for endpoint in synthesis_endpoints:
        for i, payload in enumerate(test_payloads):
            print(f"\n📤 Testing {endpoint} with payload {i+1}")
            print(f"   Payload keys: {list(payload.keys())}")
            
            response = requests.post(endpoint, headers=headers, json=payload)
            print(f"   Response: {response.status_code}")
            
            if response.status_code != 404:
                print(f"   Response: {response.text[:300]}")
                
                # Check if we got a generation_id or record_id
                try:
                    data = response.json()
                    if 'id' in data or 'generation_id' in data or 'record_id' in data:
                        print(f"   ✅ Found ID field: {data}")
                        return data
                except:
                    pass

def test_sdk_synthesis_with_custom_voice(api_key: str):
    """Test SDK synthesis methods to see if they can create custom voices."""
    print("\n🔍 Testing SDK synthesis with custom voice...")
    
    client = HumeClient(api_key=api_key)
    
    # Try synthesize_json with minimal required params
    try:
        print("\nAttempting synthesize_json...")
        # First, let's see what parameters it expects
        sig = inspect.signature(client.tts.synthesize_json)
        print(f"Required params: {sig}")
        
        # Try a simple synthesis to see the response structure
        response = client.tts.synthesize_json(
            text="Hello world",
            provider="HUME_AI"
        )
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        # Check if response has any ID we can use
        if hasattr(response, '__dict__'):
            print(f"Response attributes: {response.__dict__}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_list_tts_records(api_key: str):
    """Try to list existing TTS records to understand the structure."""
    print("\n🔍 Testing listing TTS records...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
    }
    
    # Try different patterns for listing records
    list_endpoints = [
        "https://api.hume.ai/v0/tts/records",
        "https://api.hume.ai/v0/tts/tts_records", 
        "https://api.hume.ai/v0/tts/history",
        "https://api.hume.ai/v0/tts/generations",
    ]
    
    for endpoint in list_endpoints:
        print(f"\n📤 Testing GET {endpoint}")
        response = requests.get(endpoint, headers=headers)
        print(f"   Response: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Found records endpoint!")
            try:
                data = response.json()
                print(f"   Sample data: {json.dumps(data[:1] if isinstance(data, list) else data, indent=2)[:500]}")
            except:
                print(f"   Content: {response.text[:300]}")

def main():
    """Main test function."""
    print("🎙️ Hume AI TTS Synthesis Investigation")
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
    explore_tts_synthesize_methods(api_key)
    test_tts_record_endpoints(api_key)
    test_list_tts_records(api_key)
    test_voice_cloning_via_tts_synthesis(api_key)
    test_sdk_synthesis_with_custom_voice(api_key)
    
    print("\n" + "=" * 50)
    print("🔍 TTS Investigation complete.")

if __name__ == "__main__":
    main()