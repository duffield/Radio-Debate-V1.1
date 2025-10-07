# Hume AI Voice Clone Chat App

This project records a voice sample from your microphone, uploads it to Hume AI to clone the voice (API mode), and then starts a simple chat loop that will respond using the cloned voice. It also includes a real-time voice conversation scaffold over WebSockets.

Important: your API credentials must be provided via environment variables. Do NOT hardcode them in code or commands.

Project layout:
- src/app.py — CLI entrypoint that orchestrates recording, cloning, and chat.
- src/recorder.py — microphone capture to WAV.
- src/hume_client.py — Hume API client scaffolding (voice cloning + chat/TTS placeholders + realtime launcher).
- src/realtime.py — realtime voice chat scaffold (mic -> WS, WS -> speaker).
- src/audio_utils.py — audio helpers for playback and file handling.

Setup
1) Create a virtualenv and install deps
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2) Configure secrets as environment variables (zsh)
   export HUME_API_KEY={{HUME_API_KEY}}
   export HUME_SECRET_KEY={{HUME_SECRET_KEY}}
   # Optional: region/base URL if applicable
   export HUME_API_BASE_URL=https://api.hume.ai/v0
   # Set full URLs for REST endpoints to avoid 404s on placeholders
   export HUME_VOICE_CLONE_URL=https://api.hume.ai/v0/<your-voice-clone-endpoint>
   export HUME_TTS_URL=https://api.hume.ai/v0/<your-tts-endpoint>
   # Preferred: use Hume SDK with your EVI config; no WS URL needed
   export HUME_CONFIG_ID=<your-evi-config-id>
   # Optional fallback: raw WebSocket endpoint (only needed if SDK path is disabled or fails)
   export HUME_WS_URL=wss://api.hume.ai/v0/<your-realtime-endpoint>
   # To force-disable the SDK path (for debugging)
   export HUME_DISABLE_SDK=0
   # To allow fallback to raw WebSocket if the SDK path fails
   export HUME_FALLBACK_WS=0

Note: Replace the placeholders (like {{HUME_API_KEY}}) with your actual secrets, but do not echo or log them.

3) Run
   # Record a voice sample and start the app
   python src/app.py --record-seconds 10 --output data/voice_sample.wav

   # If you already have a sample
   python src/app.py --input data/voice_sample.wav

Real-time voice conversation (scaffold)
   # After setting HUME_WS_URL, run with --realtime to stream mic audio and play responses
   python src/app.py --input data/voice_sample.wav --realtime

Current status
- Recording and audio playback are implemented.
- Real-time audio streaming scaffold implemented (protocol-agnostic). Set the correct Hume WS URL and adjust fields as needed.
- Hume REST API integration is scaffolded; insert the correct endpoints or use the official SDK.
- The Hume Python SDK is listed in requirements.txt. If present, you can prefer it over raw HTTP by replacing the REST calls in src/hume_client.py with the SDK equivalents for your product tier.

Notes
- On macOS, you may need to grant microphone permissions to the terminal app (System Settings > Privacy & Security > Microphone).
- Use headphones to avoid echo/feedback during real-time conversations.

Next steps
- Replace placeholder REST endpoints with Hume’s actual voice cloning and TTS/chat endpoints (or use their SDK).
- If Hume's realtime uses a different frame/message schema, adapt src/realtime.py config and message formats accordingly.
