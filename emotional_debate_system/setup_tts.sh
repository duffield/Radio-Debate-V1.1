#!/bin/bash

# TTS Setup Script
# Creates a Python 3.11 environment specifically for TTS

echo "🔊 Setting up TTS (Text-to-Speech) environment..."

# Check if pyenv is available
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv not found. Please install pyenv first:"
    echo "   brew install pyenv"
    echo "   Then run: pyenv install 3.11.9"
    exit 1
fi

# Check if Python 3.11 is available
if ! pyenv versions | grep -q "3.11"; then
    echo "📦 Installing Python 3.11..."
    pyenv install 3.11.9
fi

# Create TTS-specific virtual environment
echo "🔧 Creating TTS virtual environment..."
pyenv local 3.11.9
python -m venv venv_tts

# Activate and install TTS
echo "📦 Installing TTS and dependencies..."
source venv_tts/bin/activate

# Install TTS
pip install TTS

# Install other required packages
pip install -r requirements.txt

echo "✅ TTS environment ready!"
echo ""
echo "To use TTS, run:"
echo "  source venv_tts/bin/activate"
echo "  python src/main.py --audio"
