#!/bin/bash

echo "🦎 Starting Emotional AI Debate System"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

source venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🔧 Ollama not detected. Starting Ollama service..."
    echo "   (This will run in the background)"
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "✅ Ollama started"
fi

# Run the main script
python src/main.py "$@"

deactivate
