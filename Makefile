.PHONY: help debate.setup debate.env debate.run debate.audio_test \
        ollama.pull ollama.check \
        hume.opus.setup hume.opus.run \
        hume.warp.setup hume.warp.run hume.warp.run_input \
        clean

SHELL := /bin/bash
PYTHON ?= python3

# Per-app virtual environments
VENV_DEBATE := .venv_debate
VENV_HUME_OPUS := .venv_hume_opus
VENV_HUME_WARP := .venv_hume_warp

# Defaults for debate
TOPIC ?= AI ethics
ROUNDS ?= 3
AUDIO ?= 0
DEBATE_AUDIO_FLAG := $(if $(filter 1 yes true,$(AUDIO)),--audio,)

# Defaults for Hume Warp
SECONDS ?= 10
OUTPUT ?= Hume-AI-Voice-Clone-Warp/data/voice_sample.wav
INPUT ?=

help:
	@echo "Targets:"
	@echo "  debate.setup        Create venv and install deps for emotional_debate_system"
	@echo "  debate.env          Copy .env.example -> .env (non-destructive)"
	@echo "  debate.run          Run debate (vars: TOPIC=..., ROUNDS=3, AUDIO=0|1)"
	@echo "  debate.audio_test   Run audio output verification script"
	@echo "  ollama.pull         Pull default model (llama3.1:8b)"
	@echo "  ollama.check        Verify Ollama is reachable (ollama list)"
	@echo "  hume.opus.setup     Create venv and install deps for Hume Claude-Opus app"
	@echo "  hume.opus.run       Run Hume Claude-Opus app"
	@echo "  hume.warp.setup     Create venv and install deps for Hume Warp app"
	@echo "  hume.warp.run       Record sample and run Hume Warp (SECONDS, OUTPUT configurable)"
	@echo "  hume.warp.run_input Use existing sample (INPUT=path) for Hume Warp"
	@echo "  clean               Remove app virtualenvs"

# -------- Emotional Debate System --------

debate.setup:
	$(PYTHON) -m venv $(VENV_DEBATE)
	$(VENV_DEBATE)/bin/python -m pip install --upgrade pip
	$(VENV_DEBATE)/bin/pip install -r emotional_debate_system/requirements.txt
	@echo "(Optional) Copy env: cp emotional_debate_system/.env.example emotional_debate_system/.env"

debate.env:
	cp -n emotional_debate_system/.env.example emotional_debate_system/.env || true
	@echo "Edit emotional_debate_system/.env as needed"

debate.run: debate.setup
	$(VENV_DEBATE)/bin/python emotional_debate_system/src/main.py \
		--topic "$(TOPIC)" --rounds $(ROUNDS) $(DEBATE_AUDIO_FLAG)

debate.audio_test:
	$(PYTHON) emotional_debate_system/test_audio.py

# -------- Ollama helpers --------

ollama.pull:
	ollama pull llama3.1:8b

ollama.check:
	ollama list || (echo "Ollama not reachable. Start it with: ollama serve" && exit 1)

# -------- Hume AI (Claude-Opus) --------

hume.opus.setup:
	$(PYTHON) -m venv $(VENV_HUME_OPUS)
	$(VENV_HUME_OPUS)/bin/python -m pip install --upgrade pip
	$(VENV_HUME_OPUS)/bin/pip install -r Hume-AI-Voice-Clone-Claude-Opus/requirements.txt
	@echo "(Optional) cp Hume-AI-Voice-Clone-Claude-Opus/.env.example Hume-AI-Voice-Clone-Claude-Opus/.env and set secrets"

hume.opus.run: hume.opus.setup
	$(VENV_HUME_OPUS)/bin/python Hume-AI-Voice-Clone-Claude-Opus/main.py

# -------- Hume AI (Warp scaffold) --------

hume.warp.setup:
	$(PYTHON) -m venv $(VENV_HUME_WARP)
	$(VENV_HUME_WARP)/bin/python -m pip install --upgrade pip
	$(VENV_HUME_WARP)/bin/pip install -r Hume-AI-Voice-Clone-Warp/requirements.txt

# Run with recording
hume.warp.run: hume.warp.setup
	PYTHONPATH=Hume-AI-Voice-Clone-Warp/src \
	$(VENV_HUME_WARP)/bin/python Hume-AI-Voice-Clone-Warp/src/app.py \
		--record-seconds $(SECONDS) --output $(OUTPUT)

# Run with an existing input file
hume.warp.run_input: hume.warp.setup
	PYTHONPATH=Hume-AI-Voice-Clone-Warp/src \
	$(VENV_HUME_WARP)/bin/python Hume-AI-Voice-Clone-Warp/src/app.py \
		--input $(INPUT)

# -------- Cleanup --------

clean:
	rm -rf $(VENV_DEBATE) $(VENV_HUME_OPUS) $(VENV_HUME_WARP)
