#!/usr/bin/env python3
"""
Test multipart file upload approach for voice cloning
Some APIs require file uploads rather than base64 JSON
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_multipart_upload(api_key: str, voice_name: str):
    """Test voice cloning using multipart file upload."""
    print(f"\n🔄 Testing multipart file upload for voice cloning...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
        # Note: Content-Type will be set automatically for multipart
    }
    
    # Test endpoints that might accept file uploads
    upload_endpoints = [
        "https://api.hume.ai/v0/tts/voices",
        "https://api.hume.ai/v0/voice/custom_voices",
        "https://api.hume.ai/v0/tts/custom_voices",
        "https://api.hume.ai/v0/tts/voices/upload",
        "https://api.hume.ai/v0/voice/upload",
    ]
    
    for endpoint in upload_endpoints:
        print(f"\n📤 Testing multipart upload to: {endpoint}")
        
        try:
            with open("voice_recording.wav", "rb") as audio_file:
                files = {
                    'file': ('voice_recording.wav', audio_file, 'audio/wav'),
                    'name': (None, voice_name),
                    'provider': (None, 'HUME_AI')
                }
                
                response = requests.post(endpoint, headers=headers, files=files)
                print(f"   Response: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"   ✅ SUCCESS! Response: {result}")
                    return result
                elif response.status_code == 422:
                    print(f"   ⚠️  Validation error: {response.text[:200]}...")
                else:
                    print(f"   ❌ Error: {response.text[:150]}...")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def test_generation_with_file_param(api_key: str, voice_name: str):
    """Test if there's a generation endpoint that accepts files."""
    print(f"\n🔄 Testing generation endpoints with file parameter...")
    
    headers = {
        "X-Hume-Api-Key": api_key,
    }
    
    generation_endpoints = [
        "https://api.hume.ai/v0/tts/generate",
        "https://api.hume.ai/v0/tts/voice/generate", 
        "https://api.hume.ai/v0/voice/generate",
        "https://api.hume.ai/v0/tts/create_voice",
        "https://api.hume.ai/v0/voice/create",
    ]
    
    for endpoint in generation_endpoints:
        print(f"\n📤 Testing generation with file to: {endpoint}")
        
        try:
            with open("voice_recording.wav", "rb") as audio_file:
                files = {
                    'audio_file': ('voice_recording.wav', audio_file, 'audio/wav'),
                }
                data = {
                    'name': voice_name,
                    'provider': 'HUME_AI'
                }
                
                response = requests.post(endpoint, headers=headers, files=files, data=data)
                print(f"   Response: {response.status_code}")
                
                if response.status_code in [200, 201, 202]:
                    result = response.json()
                    generation_id = result.get('id') or result.get('generation_id')
                    print(f"   ✅ SUCCESS! Generation ID: {generation_id}")
                    print(f"   Full response: {result}")
                    return generation_id
                elif response.status_code == 422:
                    print(f"   ⚠️  Validation error: {response.text[:200]}...")
                else:
                    print(f"   ❌ Error: {response.text[:150]}...")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def main():
    """Main test function."""
    print("🎙️ Hume AI Multipart Upload Test")
    print("=" * 50)
    
    # Get API key
    api_key = os.environ.get("HUME_API_KEY")
    if not api_key:
        print("❌ HUME_API_KEY not found in environment")
        return
    
    # Check if audio file exists
    if not os.path.exists("voice_recording.wav"):
        print("❌ voice_recording.wav not found. Run main.py first to record audio.")
        return
    
    print(f"✅ Found voice_recording.wav")
    
    voice_name = "Test-Multipart-01"
    
    # Test direct multipart upload
    result1 = test_multipart_upload(api_key, voice_name)
    
    # Test generation with file upload
    generation_id = test_generation_with_file_param(api_key, voice_name)
    
    if result1:
        print(f"\n🎉 SUCCESS with direct upload!")
    elif generation_id:
        print(f"\n🎉 SUCCESS with generation! ID: {generation_id}")
        # Now try to create voice with this generation_id
        print("Now attempting to create voice with generation_id...")
        # (This would use the previous voice creation logic)
    else:
        print(f"\n❌ No successful upload method found")
        print("🤔 The API might have changed or require authentication/permissions")
        print("💡 Recommendation: Check Hume's latest documentation or use their web interface")

if __name__ == "__main__":
    main()