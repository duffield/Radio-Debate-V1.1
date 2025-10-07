# Hume AI Voice Cloner (Real-time)

This project records your voice, creates a custom Hume AI voice clone, builds a Hume Empathic Voice config that uses Anthropic Claude for the LLM, and then starts a real-time conversation using the cloned voice.

## Prerequisites
- macOS
- Python 3.9+
- A Hume AI API key
- PortAudio (required by PyAudio)

Install PortAudio on macOS (if you don't have it):

```
brew install portaudio
```

## Setup

1) Create the virtual environment and install dependencies

```
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

2) Configure environment variables

Copy the example and fill in your Hume API key:

```
cp .env.example .env
# then edit .env to set HUME_API_KEY
```

If you already have a Hume Empathic Voice config you want to use, set `HUME_CONFIG_ID` in `.env`. When this is set, the app will use that config directly and skip the recording/cloning/config-creation steps.

## Running

```
.venv/bin/python main.py
```

Follow the prompts to:
- Accept the voice cloning agreement
- Record ~30 seconds of your voice
- Optionally save the recording locally
- Create a custom voice and a Hume Empathic Voice config
- Start a chat using that config in real time

## Which config ID does this target?

Behavior now depends on whether `HUME_CONFIG_ID` is set:
- If `HUME_CONFIG_ID` is set in `.env`, the app uses that existing config directly and starts the conversation.
- Otherwise, the app:
  1. Creates a custom voice from your recording
  2. Creates a new Empathic Voice config referencing that voice and Anthropic Claude (model_id: `claude-3-5-sonnet-20241022`)
  3. Uses the newly created config's ID to start the conversation

## Override voice non-destructively (HUME_VOICE_ID)

You can reuse your character prompts/LLM from an existing config while changing voices just for this run:

- Set both env vars:
  - HUME_CONFIG_ID=YOUR_TEMPLATE_CONFIG_ID
  - HUME_VOICE_ID=VOICE_ID_TO_USE_FOR_THIS_SESSION
- The app will fetch the template config, create a derived config with the same prompt and language_model but with the new voice, and start the session using that derived config.
- Your original config stays unchanged.

## Notes on dependencies

- PyAudio requires PortAudio headers; if installation fails, run `brew install portaudio` and then reinstall PyAudio.
- The `hume` Python SDK is used for realtime voice; REST calls are used for voice and config creation.
- `python-dotenv` is used to load `.env` automatically.

## Troubleshooting

- PyAudio install fails:
  - Ensure Homebrew is installed and run `brew install portaudio`
  - Try: `.venv/bin/python -m pip install --no-cache-dir pyaudio`

- Hume errors creating voice/config:
  - Double-check `HUME_API_KEY`
  - Ensure your account has access to the necessary APIs
