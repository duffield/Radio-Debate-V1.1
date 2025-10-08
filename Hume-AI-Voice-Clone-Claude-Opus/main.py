import asyncio
import base64
import json
import os
import time
import wave
from typing import Optional

import pyaudio
import requests
from hume import AsyncHumeClient
from hume.empathic_voice.chat.socket_client import ChatConnectOptions
from hume.empathic_voice.types import ToolCallMessage, UserInput
import numpy as np
from dotenv import load_dotenv


class HumeVoiceCloneApp:
    def __init__(self, api_key: str, secret_key: str = None):
        """Initialize the Hume AI Voice Clone App.
        
        Args:
            api_key: Your Hume AI API key
            secret_key: Your Hume AI Secret key (for websocket connections)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.hume.ai/v0"
        self.headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        self.voice_client = None
        self.config_id = None
        
    def record_audio(self, duration: int = 10, sample_rate: int = 16000) -> bytes:
        """Record audio from the user's microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate for recording
            
        Returns:
            WAV audio data as bytes
        """
        print(f"\n🎤 Please speak clearly for {duration} seconds...")
        print("Recording will start in 3 seconds...")
        time.sleep(3)
        
        # Audio recording parameters
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Start recording
        stream = p.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk
        )
        
        print("🔴 Recording...")
        frames = []
        
        for i in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
            
            # Show progress
            if i % (sample_rate // chunk) == 0:
                remaining = duration - (i // (sample_rate // chunk))
                print(f"   {remaining} seconds remaining...")
        
        print("✅ Recording complete!")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Convert to WAV format
        wav_buffer = self._create_wav_buffer(frames, sample_rate, channels, format)
        return wav_buffer
    
    def _create_wav_buffer(self, frames, sample_rate, channels, format) -> bytes:
        """Create a WAV buffer from audio frames.
        
        Returns:
            WAV file as bytes
        """
        import io
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(format))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        
        wav_buffer.seek(0)
        return wav_buffer.read()
    
    def create_voice_clone(self, audio_data: bytes, voice_name: str) -> str:
        """Create a voice clone using the recorded audio.
        
        Args:
            audio_data: WAV audio data
            voice_name: Name for the cloned voice
            
        Returns:
            Voice ID of the created clone
        """
        print("\n🔄 Creating voice clone...")
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Create voice clone request
        url = f"{self.base_url}/voice/custom_voices"
        
        payload = {
            "name": voice_name,
            "base_voice": "ITO",  # You can change this base voice
            "parameters": {
                "gender": -5,  # Adjust based on recorded voice
                "huskiness": -5,
                "nasality": -8,
                "pitch": -5
            },
            "samples": [
                {
                    "data": audio_base64,
                    "mime_type": "audio/wav"
                }
            ]
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            voice_id = result.get("id")
            print(f"✅ Voice clone created successfully! Voice ID: {voice_id}")
            return voice_id
        else:
            print(f"❌ Error creating voice clone: {response.text}")
            raise Exception(f"Failed to create voice clone: {response.status_code}")
    
    def create_config_with_voice(self, voice_id: str, config_name: str) -> str:
        """Create a new config using the cloned voice.
        
        Args:
            voice_id: ID of the cloned voice
            config_name: Name for the new config
            
        Returns:
            Config ID
        """
        print(f"\n🔧 Creating config with cloned voice...")
        
        url = f"{self.base_url}/empathic_voice/configs"
        
        payload = {
            "name": config_name,
            "prompt": {
                "text": "You are a helpful and empathetic AI assistant. Respond naturally and conversationally.",
                "version": 0
            },
            "voice": {
                "provider": "HUME_AI",
                "voice_id": voice_id
            },
            "language_model": {
                "provider": "ANTHROPIC",
                "model_id": "claude-3-5-sonnet-20241022"  # Or your preferred model
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            config_id = result.get("id")
            print(f"✅ Config created successfully! Config ID: {config_id}")
            return config_id
        else:
            print(f"❌ Error creating config: {response.text}")
            raise Exception(f"Failed to create config: {response.status_code}")
    
    def fetch_config(self, config_id: str) -> dict:
        """Fetch a Hume Empathic Voice config by ID."""
        url = f"{self.base_url}/empathic_voice/configs/{config_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch config {config_id}: {response.status_code} {response.text}")

    def create_config_from_template_with_voice(self, template_cfg: dict, new_voice_id: str, name_suffix: Optional[str] = None) -> str:
        """Create a new config from a template config, overriding only the voice."""
        if not name_suffix:
            name_suffix = f"Derived_{int(time.time())}"
        payload = {
            "name": f"{template_cfg.get('name', 'Config')}_{name_suffix}",
            "prompt": template_cfg.get("prompt", {}),
            "language_model": template_cfg.get("language_model", {}),
            "voice": {
                "provider": "HUME_AI",
                "voice_id": new_voice_id,
            },
        }
        url = f"{self.base_url}/empathic_voice/configs"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            new_config_id = result.get("id")
            print(f"✅ Derived config created with new voice. Config ID: {new_config_id}")
            return new_config_id
        else:
            print(f"❌ Error creating derived config: {response.text}")
            raise Exception(f"Failed to create derived config: {response.status_code}")
    
    async def start_conversation(self, config_id: str):
        """Start a conversation with the cloned voice.
        
        Args:
            config_id: Configuration ID to use
        """
        print("\n💬 Starting conversation with your cloned voice...")
        print("Type 'quit' to exit the conversation.\n")
        
        # Initialize the voice client
        client = AsyncHumeClient(api_key=self.api_key)
        
        # Create connection options dictionary
        connect_options = {
            "config_id": config_id,
        }
        if self.secret_key:
            connect_options["secret_key"] = self.secret_key
        
        # Connect with the custom config
        async with client.empathic_voice.chat.connect(connect_options) as socket:
            await self._handle_conversation(socket)
    
    async def _handle_conversation(self, socket):
        """Handle the conversation loop with the socket."""
        print("Connected! You can start chatting now.\n")
        
        while True:
            # Get user input
            user_message = input("You: ")
            
            if user_message.lower() == 'quit':
                print("\n👋 Ending conversation...")
                break
            
            # Send message to the assistant
            try:
                # Create a proper UserInput object
                user_input = UserInput(text=user_message)
                await socket.send_user_input(user_input)
            except Exception as e:
                print(f"\u274c Error sending message: {e}")
                continue
            
            # Receive and print response
            print("Assistant: ", end="", flush=True)
            
            try:
                async for message in socket:
                    print(f"\n[DEBUG] Message type: {type(message)}")
                    print(f"[DEBUG] Message dir: {[attr for attr in dir(message) if not attr.startswith('_')][:10]}")
                    if hasattr(message, '__dict__'):
                        print(f"[DEBUG] Message dict: {message.__dict__}")
                    
                    if isinstance(message, UserInput):
                        # Handle user interruption
                        continue
                    elif isinstance(message, ToolCallMessage):
                        # Handle tool calls if configured
                        continue
                    else:
                        # Print the assistant's response
                        if hasattr(message, 'content'):
                            print(message.content, end="", flush=True)
                        elif hasattr(message, 'text'):
                            print(message.text, end="", flush=True)
                        elif isinstance(message, dict) and 'text' in message:
                            print(message['text'], end="", flush=True)
                        # Don't break immediately - let's see more messages
            except Exception as e:
                print(f"\u274c Error receiving response: {e}")
            
            print("\n")
    
    def get_user_agreement(self) -> bool:
        """Get user agreement for voice recording and cloning.
        
        Returns:
            True if user agrees, False otherwise
        """
        print("\n" + "="*60)
        print("VOICE CLONING AGREEMENT")
        print("="*60)
        print("""
This application will:
1. Record 30 seconds of your voice
2. Create a voice clone using Hume AI's technology
3. Use this cloned voice for the AI assistant in this session

Your voice data will be:
- Processed by Hume AI's secure servers
- Used only for this application session
- Subject to Hume AI's privacy policy

By proceeding, you confirm that:
- You consent to having your voice recorded and cloned
- You understand how your voice data will be used
- You are the person whose voice is being recorded
        """)
        print("="*60)
        
        response = input("\nDo you agree to proceed? (yes/no): ").lower().strip()
        return response == 'yes' or response == 'y'
    
    async def run(self):
        """Main application flow."""
        print("\n🎙️ Welcome to Hume AI Voice Cloning App!")
        print("="*60)

        # If a pre-existing config ID is provided, use it directly
        existing_config_id = os.environ.get("HUME_CONFIG_ID", "").strip()
        voice_override_id = os.environ.get("HUME_VOICE_ID", "").strip()
        if existing_config_id:
            if voice_override_id:
                print(f"\nUsing template config {existing_config_id} with overridden voice {voice_override_id} (non-destructive).")
                try:
                    template_cfg = self.fetch_config(existing_config_id)
                    derived_config_id = self.create_config_from_template_with_voice(
                        template_cfg, voice_override_id
                    )
                    await self.start_conversation(derived_config_id)
                except Exception as e:
                    print(f"\n❌ Failed to create or use derived config: {e}")
                return
            else:
                print(f"\nUsing existing Hume config ID from environment: {existing_config_id}")
                try:
                    await self.start_conversation(existing_config_id)
                except Exception as e:
                    print(f"\n❌ Failed to start conversation with existing config: {e}")
                return
        
        # Get user agreement
        if not self.get_user_agreement():
            print("\n❌ User agreement not provided. Exiting...")
            return
        
        try:
            # Step 1: Record user's voice
            audio_data = self.record_audio(duration=30)
            
            # Optional: Save the recording
            save_recording = input("\nWould you like to save the recording locally? (yes/no): ").lower()
            if save_recording in ['yes', 'y']:
                with open("voice_recording.wav", "wb") as f:
                    f.write(audio_data)
                print("✅ Recording saved as 'voice_recording.wav'")
            
            # Step 2: Create voice clone
            voice_name = input("\nEnter a name for your voice clone: ").strip()
            if not voice_name:
                voice_name = f"Voice_Clone_{int(time.time())}"
            
            voice_id = self.create_voice_clone(audio_data, voice_name)
            
            # Step 3: Create config with the cloned voice
            config_name = f"Config_{voice_name}"
            config_id = self.create_config_with_voice(voice_id, config_name)
            
            # Step 4: Start conversation
            await self.start_conversation(config_id)
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()


# Additional utility functions
def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['pyaudio', 'hume', 'requests', 'numpy', 'dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them using:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


async def main():
    """Main entry point for the application."""
    # Load environment variables from .env if present
    load_dotenv()

    # Check dependencies
    if not check_dependencies():
        return
    
    # Get API key and secret key
    api_key = os.environ.get("HUME_API_KEY")
    secret_key = os.environ.get("HUME_SECRET_KEY")
    
    if not api_key:
        api_key = input("Please enter your Hume AI API key: ").strip()
    
    if not secret_key:
        secret_key = input("Please enter your Hume AI Secret key (optional, press Enter to skip): ").strip()
        if not secret_key:
            secret_key = None
    
    if not api_key:
        print("❌ API key is required to proceed.")
        return
    
    # Create and run the app
    app = HumeVoiceCloneApp(api_key, secret_key)
    await app.run()


if __name__ == "__main__":
    # Run the application
    asyncio.run(main())