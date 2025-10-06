#!/bin/bash

echo "🔧 Setting up Emotional AI Debate System"
echo "="*60

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing..."
    brew install ollama
fi

# Check if espeak-ng is installed  
if ! command -v espeak-ng &> /dev/null; then
    echo "❌ espeak-ng not found. Installing..."
    brew install espeak-ng
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies (this may take 5-10 minutes)..."
pip install -r requirements.txt

echo ""
echo "🤖 Checking Ollama models..."
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "📥 Downloading llama3.1:8b model (~5GB, may take 5-10 minutes)..."
    ollama pull llama3.1:8b
else
    echo "✅ llama3.1:8b already installed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. source venv/bin/activate"
echo "2. ollama serve  # In a separate terminal"
echo "3. python src/main.py"
