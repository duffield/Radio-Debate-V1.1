# Radio-Debate-V1.1

This repository contains three standalone Python apps. See WARP.md for full guidance.

Apps
- emotional_debate_system
  - Entry: emotional_debate_system/src/main.py
  - Purpose: Two-agent emotional AI debate with OSC streaming to TouchDesigner and optional local TTS.
  - Backend: Local Ollama LLM (llama3.1:8b by default).

- Hume-AI-Voice-Clone-Claude-Opus
  - Entry: Hume-AI-Voice-Clone-Claude-Opus/main.py
  - Purpose: Record voice, clone with Hume API, create Empathic Voice config (Claude), and start a realtime chat.

- Hume-AI-Voice-Clone-Warp
  - Entry: Hume-AI-Voice-Clone-Warp/src/app.py
  - Purpose: Scaffolded Hume voice clone + chat with REST/WS placeholders and a realtime mode.

Quickstart (Makefile)
- make help
- make debate.setup && make ollama.pull && make debate.run TOPIC="AI ethics" ROUNDS=3 AUDIO=1
- make debate.audio_test
- make hume.opus.setup && make hume.opus.run
- make hume.warp.setup && make hume.warp.run SECONDS=10

Notes
- Each app has its own requirements.txt. Virtualenvs are created per-app by the Makefile.
- Configure secrets for Hume apps via environment variables or .env (see app READMEs).