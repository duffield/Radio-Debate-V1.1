# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository overview
- This repo contains three Python applications developed side-by-side:
  - emotional_debate_system: Emotional AI debate with OSC streaming to TouchDesigner, optional local TTS, and Ollama-backed LLM.
  - Hume-AI-Voice-Clone-Claude-Opus: Record voice, create a Hume Empathic Voice config (uses Anthropic Claude), and start a realtime chat.
  - Hume-AI-Voice-Clone-Warp: A scaffolded Hume voice clone + chat app with explicit REST/WS placeholders.
- There is no mono-repo build; each app has its own requirements.txt and can be run independently.

Prerequisites
- macOS, Python 3.13+ for emotional_debate_system (as noted in its README). Hume apps run on Python 3.9+.
- Recommended: create and activate a Python virtual environment before installing each app’s dependencies.

Common commands by app

emotional_debate_system
Environment setup
- Create and activate a venv, then install dependencies:
  - python3 -m venv .venv
  - source .venv/bin/activate
  - pip install -r emotional_debate_system/requirements.txt
- Optional: copy env template and adjust values
  - cp emotional_debate_system/.env.example emotional_debate_system/.env

Run the debate (CLI)
- Start the LLM backend (Ollama) in another terminal:
  - ollama serve
  - ollama pull llama3.1:8b
- Run the debate app:
  - python emotional_debate_system/src/main.py --topic "Your topic" --rounds 3 [--audio | --no-audio]
  - Examples:
    - python emotional_debate_system/src/main.py
    - python emotional_debate_system/src/main.py --topic "AI ethics" --rounds 4 --audio

Audio/OSC notes
- Audio synthesis uses macOS "say" when available; otherwise a simplified TTS writes text files to data/audio_output/.
- OSC is sent to 127.0.0.1:5005 at 30 FPS by default (configurable via .env).

Ad-hoc tests and utilities
- Audio output verification:
  - python emotional_debate_system/test_audio.py
- There is no unified pytest configuration detected for this app; run individual scripts directly.

Key configuration
- Env file (emotional_debate_system/.env) supports:
  - OLLAMA_HOST, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
  - EMOTION_MODEL, EMOTION_THRESHOLD, EMOTION_DEVICE
  - TTS_ENGINE, TTS_MODEL, TTS_SPEED, SAVE_AUDIO
  - OSC_IP, OSC_PORT, OSC_FPS
  - DEBUG_MODE

Hume-AI-Voice-Clone-Claude-Opus
Environment setup
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r Hume-AI-Voice-Clone-Claude-Opus/requirements.txt
- cp Hume-AI-Voice-Clone-Claude-Opus/.env.example Hume-AI-Voice-Clone-Claude-Opus/.env
- Set secrets in the .env (do not print them). Required: HUME_API_KEY; optional: HUME_SECRET_KEY, HUME_CONFIG_ID, HUME_VOICE_ID.

Run
- python Hume-AI-Voice-Clone-Claude-Opus/main.py
- Behavior:
  - If HUME_CONFIG_ID is set, uses that config directly.
  - If HUME_CONFIG_ID and HUME_VOICE_ID are both set, derives a temporary config that reuses prompt/LLM with the new voice.
  - Otherwise, records voice, creates a custom voice, creates a config with Anthropic Claude (claude-3-5-sonnet-20241022), then starts a chat.

Ad-hoc tests
- Direct API and SDK probing for voice cloning:
  - python Hume-AI-Voice-Clone-Claude-Opus/test_voice_clone.py

Key configuration
- .env keys:
  - HUME_API_KEY (required), HUME_SECRET_KEY (optional)
  - HUME_CONFIG_ID (optional), HUME_VOICE_ID (optional)

Hume-AI-Voice-Clone-Warp
Environment setup
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r Hume-AI-Voice-Clone-Warp/requirements.txt
- Provide environment variables in your shell (do not echo secrets):
  - export HUME_API_KEY={{HUME_API_KEY}}
  - export HUME_SECRET_KEY={{HUME_SECRET_KEY}}
  - export HUME_API_BASE_URL=https://api.hume.ai/v0
  - Optional placeholders (replace with real product endpoints if not using the SDK):
    - export HUME_VOICE_CLONE_URL=https://api.hume.ai/v0/<your-voice-clone-endpoint>
    - export HUME_TTS_URL=https://api.hume.ai/v0/<your-tts-endpoint>
    - export HUME_CONFIG_ID=<your-evi-config-id>
    - export HUME_WS_URL=wss://api.hume.ai/v0/<your-realtime-endpoint>
    - export HUME_DISABLE_SDK=0
    - export HUME_FALLBACK_WS=0

Run
- Record a sample and run:
  - python Hume-AI-Voice-Clone-Warp/src/app.py --record-seconds 10 --output data/voice_sample.wav
- Use an existing sample:
  - python Hume-AI-Voice-Clone-Warp/src/app.py --input data/voice_sample.wav
- Realtime scaffold:
  - python Hume-AI-Voice-Clone-Warp/src/app.py --input data/voice_sample.wav --realtime

Testing and linting
- No repo-wide test runner or linter configuration is present.
- Tests provided here are script-style (e.g., test_audio.py, Hume test_* files) and can be executed directly with python.

High-level architecture

emotional_debate_system
- Entry point: src/main.py
  - DebateSystem orchestrates a two-agent debate loop over N rounds. Agents alternate speaking about a topic.
  - LLM: OllamaLLM (src/llm/ollama_provider.py)
    - Uses a local Ollama server via ollama.Client, character-specific system prompts, and simple keyword heuristics for initial emotion guesses.
    - is_available() checks connectivity by listing models; the app exits if Ollama isn’t running.
  - Emotion analysis: EmotionDetector (src/emotion/detector.py)
    - Hugging Face transformers pipeline (SamLowe/roberta-base-go_emotions) on CPU/MPS/CUDA depending on availability.
    - enrich_emotions() replaces the response’s emotions with model outputs above threshold and recomputes valence/arousal.
  - TTS: MacOSTTS then fallback to CoquiTTS (src/tts/macos_provider.py, src/tts/coqui_provider.py)
    - MacOSTTS uses the macOS say command to both speak and save AIFF files (character-specific voice mapping). If unavailable, CoquiTTS simplified mode writes a text file instead of audio.
  - OSC streaming: OSCStreamer (src/streaming/osc_streamer.py)
    - Sends per-emotion intensities, valence, arousal, and primary_emotion to TouchDesigner via python-osc.
  - Configuration: config/config.py (pydantic models)
    - Loads .env with defaults, creates data directories (data/audio_output, data/debate_logs), and exposes llm/emotion/tts/osc/system config.

Hume-AI-Voice-Clone-Claude-Opus
- main.py exposes HumeVoiceCloneApp with a guided flow:
  - record_audio() with PyAudio → create_voice_clone() via REST → create_config_with_voice() → start_conversation() over AsyncHumeClient empathic_voice.chat sockets.
  - Supports existing config usage and non-destructive voice overrides by deriving a config from a template.
  - test_voice_clone.py explores multiple endpoints/payloads for cloning to adapt to API changes.

Hume-AI-Voice-Clone-Warp
- src/app.py coordinates recording (src/recorder.py), optional playback (src/audio_utils.py), a stub Hume client (src/hume_client.py), and optional realtime (src/realtime.py).
- Explicit placeholders for REST/WS endpoints are present to be replaced or superseded by the official SDK paths.

Notes and caveats
- The emotional_debate_system README references shell launchers (quick_debate.sh, start_debate.sh, run.sh) that are not present in this repository. Use the Python entry point instead: python emotional_debate_system/src/main.py.
- Ensure Ollama is running and the model (default: llama3.1:8b) is pulled before starting the debate app.
- macOS microphone/speaker permissions may be required for Hume apps and for say/afplay where used.
