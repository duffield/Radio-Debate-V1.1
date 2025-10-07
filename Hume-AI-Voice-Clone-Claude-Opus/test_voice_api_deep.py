#!/usr/bin/env python3
"""
Deep dive test to understand Hume's voice cloning API workflow
Focus on finding how to get a generation_id
"""

import os
import base64
import requests
import json
from dotenv import load_dotenv
from hume import HumeClient

# Load environment variables
load_dotenv()

def test_list_available_endpoints(api_key: str):
    """Try to discover available endpoints by testing common patterns."""
    print("\n🔍 Testing API endpoint discovery...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
    }
    
    # Test base endpoints to see what's available
    base_endpoints = [
        "https://api.hume.ai/v0",
        "https://api.hume.ai/v0/tts",
        "https://api.hume.ai/v0/voice",
        "https://api.hume.ai/v0/empathic_voice",
    ]
    
    for endpoint in base_endpoints:
        print(f"\n📤 Testing GET {endpoint}")
        response = requests.get(endpoint, headers=headers)
        print(f"   Response: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Content: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"   Content: {response.text[:200]}")

def test_create_voice_with_dummy_generation_id(api_key: str):
    """Test what happens when we provide a dummy generation_id."""
    print("\n🔍 Testing voice creation with dummy generation_id...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Try with different generation_id formats
    test_payloads = [
        {
            "generation_id": "test-generation-123",
            "name": "Test Voice"
        },
        {
            "generation_id": "00000000-0000-0000-0000-000000000000",
            "name": "Test Voice UUID"
        },
        {
            "generation_id": "",
            "name": "Test Voice Empty"
        }
    ]
    
    for payload in test_payloads:
        print(f"\n   Testing with generation_id: {payload['generation_id']}")
        response = requests.post(
            "https://api.hume.ai/v0/tts/voices",
            headers=headers,
            json=payload
        )
        print(f"   Response: {response.status_code}")
        print(f"   Message: {response.text[:300]}")
        
        # If we get a different error than 422, we might learn something
        if response.status_code != 422:
            print(f"   🔍 Different error! This tells us something...")

def test_sdk_detailed_exploration(api_key: str):
    """Use SDK to explore all available methods in detail."""
    print("\n🔍 Detailed SDK exploration...")
    
    client = HumeClient(api_key=api_key)
    
    # Check if there's a way to list generations
    print("\n=== Checking for generation-related methods ===")
    
    # Check TTS client for any hidden methods
    import inspect
    
    print("\nTTS Client methods (including private):")
    for name, method in inspect.getmembers(client.tts):
        if callable(method):
            print(f"  {name}: {type(method)}")
            
    print("\nTTS Voices Client methods (including private):")
    for name, method in inspect.getmembers(client.tts.voices):
        if callable(method):
            print(f"  {name}: {type(method)}")
            
            # Check method signature for 'create'
            if name == 'create':
                sig = inspect.signature(method)
                print(f"    Signature: {sig}")
                print(f"    Docstring: {method.__doc__[:200] if method.__doc__ else 'No docstring'}")

def test_expression_measurement_for_voice(api_key: str):
    """Check if voice cloning might be under expression_measurement."""
    print("\n🔍 Checking expression_measurement client...")
    
    client = HumeClient(api_key=api_key)
    
    # Explore expression_measurement
    print("Expression Measurement attributes:")
    print([attr for attr in dir(client.expression_measurement) if not attr.startswith('_')])
    
    # Check for any voice-related methods
    for attr in dir(client.expression_measurement):
        if 'voice' in attr.lower() or 'audio' in attr.lower():
            print(f"  Found: {attr}")

def test_raw_api_with_different_versions(api_key: str):
    """Test if there are different API versions available."""
    print("\n🔍 Testing different API versions...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
    }
    
    # Test different version patterns
    versions = ["v0", "v1", "v2", "beta", "v0-beta", "v1-beta"]
    
    for version in versions:
        url = f"https://api.hume.ai/{version}/tts/voices"
        print(f"\n📤 Testing {url}")
        
        response = requests.get(url, headers=headers, params={"provider": "HUME_AI"})
        print(f"   Response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Version {version} works!")
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"   Sample voice: {data[0] if isinstance(data, list) else data}")
            except:
                pass

def test_check_api_documentation_endpoint(api_key: str):
    """Check if there's an API documentation or OpenAPI spec endpoint."""
    print("\n🔍 Checking for API documentation endpoints...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
    }
    
    doc_endpoints = [
        "https://api.hume.ai/docs",
        "https://api.hume.ai/v0/docs",
        "https://api.hume.ai/openapi.json",
        "https://api.hume.ai/v0/openapi.json",
        "https://api.hume.ai/swagger.json",
        "https://api.hume.ai/api-docs",
        "https://api.hume.ai/v0/api-docs",
    ]
    
    for endpoint in doc_endpoints:
        print(f"\n📤 Testing {endpoint}")
        response = requests.get(endpoint, headers=headers)
        print(f"   Response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Found documentation!")
            try:
                data = response.json()
                # Look for voice-related paths
                if 'paths' in data:
                    voice_paths = [path for path in data['paths'] if 'voice' in path.lower()]
                    print(f"   Voice-related paths: {voice_paths[:5]}")
            except:
                print(f"   Content preview: {response.text[:200]}")

def main():
    """Main test function."""
    print("🎙️ Hume AI Voice Cloning API Deep Dive")
    print("=" * 50)
    
    # Get API key
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found in environment")
        return
    
    # Run all tests
    test_list_available_endpoints(api_key)
    test_create_voice_with_dummy_generation_id(api_key)
    test_sdk_detailed_exploration(api_key)
    test_expression_measurement_for_voice(api_key)
    test_raw_api_with_different_versions(api_key)
    test_check_api_documentation_endpoint(api_key)
    
    print("\n" + "=" * 50)
    print("🔍 Analysis complete. Check results above for clues.")

if __name__ == "__main__":
    main()