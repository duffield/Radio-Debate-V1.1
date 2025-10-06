#!/bin/bash

echo "📝 Creating configuration files..."

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core LLM
ollama>=0.1.0

# Emotion Detection
transformers>=4.35.0
torch>=2.1.0
sentencepiece>=0.1.99

# Text-to-Speech (Local)
TTS>=0.22.0
pydub>=0.25.1
soundfile>=0.12.1

# OSC Streaming
python-osc>=1.8.3

# Utilities
pydantic>=2.5.0
python-dotenv>=1.0.0
numpy>=1.24.0
scipy>=1.11.0
EOF

echo "✅ Created requirements.txt"

# Create .env.example
cat > .env.example << 'EOF'
# LLM Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=150

# Emotion Detection
EMOTION_MODEL=SamLowe/roberta-base-go_emotions
EMOTION_THRESHOLD=0.3
EMOTION_DEVICE=cpu

# TTS Configuration
TTS_ENGINE=local
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_SPEED=1.0
SAVE_AUDIO=true

# OSC Streaming
OSC_IP=127.0.0.1
OSC_PORT=5005
OSC_FPS=30

# System
DEBUG_MODE=true
SAVE_LOGS=true
EOF

echo "✅ Created .env.example"

# Copy to .env
cp .env.example .env
echo "✅ Created .env (you can edit this later)"

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment
.env
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Models
models/*.pt
models/*.onnx
models/*.bin

# Data
data/audio_output/*.wav
data/audio_output/*.mp3
data/debate_logs/*.json

# IDE
.vscode/
.idea/
*.swp
.cursor/

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
EOF

echo "✅ Created .gitignore"

# Create config/config.py
cat > config/config.py << 'EOF'
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal

# Load environment variables
load_dotenv()

class LLMConfig(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
    model: str = Field(default_factory=lambda: os.getenv('OLLAMA_MODEL', 'llama3.1:8b'))
    temperature: float = Field(default_factory=lambda: float(os.getenv('LLM_TEMPERATURE', '0.7')))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv('LLM_MAX_TOKENS', '150')))

class EmotionConfig(BaseModel):
    model: str = Field(default_factory=lambda: os.getenv('EMOTION_MODEL', 'SamLowe/roberta-base-go_emotions'))
    threshold: float = Field(default_factory=lambda: float(os.getenv('EMOTION_THRESHOLD', '0.3')))
    device: str = Field(default_factory=lambda: os.getenv('EMOTION_DEVICE', 'cpu'))

class TTSConfig(BaseModel):
    engine: str = Field(default_factory=lambda: os.getenv('TTS_ENGINE', 'local'))
    model: str = Field(default_factory=lambda: os.getenv('TTS_MODEL', 'tts_models/en/ljspeech/tacotron2-DDC'))
    speed: float = Field(default_factory=lambda: float(os.getenv('TTS_SPEED', '1.0')))
    save_audio: bool = Field(default_factory=lambda: os.getenv('SAVE_AUDIO', 'true').lower() == 'true')

class OSCConfig(BaseModel):
    ip: str = Field(default_factory=lambda: os.getenv('OSC_IP', '127.0.0.1'))
    port: int = Field(default_factory=lambda: int(os.getenv('OSC_PORT', '5005')))
    fps: int = Field(default_factory=lambda: int(os.getenv('OSC_FPS', '30')))

class SystemConfig(BaseModel):
    debug: bool = Field(default_factory=lambda: os.getenv('DEBUG_MODE', 'true').lower() == 'true')
    project_root: Path = Path(__file__).parent.parent
    audio_output_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "audio_output")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "data" / "debate_logs")
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    emotion: EmotionConfig = Field(default_factory=EmotionConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    osc: OSCConfig = Field(default_factory=OSCConfig)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Create directories
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

# Global config instance
config = SystemConfig()
EOF

echo "✅ Created config/config.py"

echo ""
echo "🎉 Configuration files created!"
echo ""
echo "Files created:"
echo "  - requirements.txt"
echo "  - .env.example"
echo "  - .env"
echo "  - .gitignore"
echo "  - config/config.py"