#!/bin/bash

# Quick Debate Launcher
# Simple one-command script to start a debate

echo "🦎 Quick Emotional AI Debate"
echo "============================"
echo ""

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Please run this from the emotional_debate_system directory"
    exit 1
fi

# Get topic from user or use default
if [ -z "$1" ]; then
    echo "Enter debate topic (or press Enter for default):"
    read -r topic
    if [ -z "$topic" ]; then
        topic="Should we worry about shapeshifting lizard people controlling world governments?"
    fi
else
    topic="$1"
fi

echo ""
echo "🎭 Starting debate: '$topic'"
echo "Press Ctrl+C to stop"
echo ""

# Run the debate
./start_debate.sh --topic "$topic" --rounds 3
