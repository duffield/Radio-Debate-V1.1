#!/bin/bash

# Emotional AI Debate System - Project Creator
# Run this to set up the complete local-first system

PROJECT_NAME="emotional_debate_system"
echo "🦎 Creating Emotional AI Debate System: $PROJECT_NAME"

# Create project directory
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p src/{llm,emotion,tts,streaming,utils}
mkdir -p {config,data/{audio_output,debate_logs},tests,models}

# Create __init__.py files
touch src/__init__.py
touch src/llm/__init__.py
touch src/emotion/__init__.py
touch src/tts/__init__.py
touch src/streaming/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

echo "✅ Project structure created!"
echo ""
echo "📂 Directory tree:"
tree -L 2 -I '__pycache__|*.pyc' . || ls -R

echo ""
echo "Next: Run the individual file creation scripts"