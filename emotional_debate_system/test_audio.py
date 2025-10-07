#!/usr/bin/env python3
"""
Audio Test Script - Test different methods of playing audio on macOS
"""

import subprocess
import tempfile
import os

def test_system_say():
    """Test system say command"""
    print("🔊 Testing system 'say' command...")
    try:
        subprocess.run(["say", "Testing audio output. Can you hear this?"], check=True, timeout=10)
        print("✅ System say command works!")
        return True
    except Exception as e:
        print(f"❌ System say failed: {e}")
        return False

def test_afplay_with_test_file():
    """Test afplay with a generated test file"""
    print("🔊 Testing afplay with temporary file...")
    try:
        # Create a temporary WAV file using say
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate a test audio file
        subprocess.run([
            "say", "-o", temp_path, 
            "Testing afplay audio output. Can you hear this synthesized voice?"
        ], check=True)
        
        # Play it with afplay
        print(f"   Playing: {temp_path}")
        subprocess.run(["afplay", temp_path], check=True, timeout=15)
        
        # Clean up
        os.unlink(temp_path)
        print("✅ afplay works!")
        return True
        
    except Exception as e:
        print(f"❌ afplay test failed: {e}")
        return False

def test_afplay_with_device():
    """Test afplay with specific audio device"""
    print("🔊 Testing afplay with device selection...")
    try:
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        subprocess.run([
            "say", "-o", temp_path, 
            "Testing device-specific audio output."
        ], check=True)
        
        # Try to play to internal speakers (if available)
        try:
            subprocess.run(["afplay", "-d", "Built-in Output", temp_path], check=True, timeout=10)
            print("✅ Built-in Output works!")
            return True
        except:
            # Try without device specification
            subprocess.run(["afplay", temp_path], check=True, timeout=10)
            print("✅ Default afplay works!")
            return True
            
    except Exception as e:
        print(f"❌ Device-specific afplay failed: {e}")
        return False
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def show_audio_devices():
    """Show available audio devices"""
    print("🎵 Available Audio Devices:")
    print("=" * 50)
    try:
        result = subprocess.run([
            "system_profiler", "SPAudioDataType"
        ], capture_output=True, text=True)
        
        lines = result.stdout.split('\n')
        current_device = None
        
        for line in lines:
            if ':' in line and not line.strip().startswith('Default') and not line.strip().startswith('Input') and not line.strip().startswith('Output'):
                if line.strip().endswith(':'):
                    current_device = line.strip()[:-1]
                    print(f"\n📱 {current_device}")
            elif 'Default Output Device: Yes' in line:
                print(f"   ✅ DEFAULT OUTPUT")
            elif 'Output Channels:' in line:
                channels = line.split(':')[1].strip()
                print(f"   🔊 {channels} output channels")
                
    except Exception as e:
        print(f"❌ Could not list devices: {e}")

def main():
    print("🎭 Audio Output Test")
    print("=" * 50)
    
    # Show available devices
    show_audio_devices()
    
    print("\n🧪 Running Audio Tests...")
    print("=" * 50)
    
    # Test different methods
    methods = [
        ("System Say", test_system_say),
        ("afplay (temp file)", test_afplay_with_test_file),
        ("afplay (device)", test_afplay_with_device),
    ]
    
    working_methods = []
    
    for name, test_func in methods:
        print(f"\n📊 Testing: {name}")
        print("-" * 30)
        if test_func():
            working_methods.append(name)
    
    print(f"\n🏁 Results:")
    print("=" * 50)
    if working_methods:
        print("✅ Working methods:")
        for method in working_methods:
            print(f"   • {method}")
    else:
        print("❌ No audio methods worked")
        print("💡 Try checking your audio settings or connecting headphones")

if __name__ == "__main__":
    main()