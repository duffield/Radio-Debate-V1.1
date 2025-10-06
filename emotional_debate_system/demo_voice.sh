#!/bin/bash

# Voice Synthesis Demo Script
# Shows the difference between text-only and voice-enabled modes

echo "🎭 Emotional AI Debate System - Voice Demo"
echo "=========================================="
echo ""

echo "This demo will show you:"
echo "1. Text-only mode (fast, no audio)"
echo "2. Voice synthesis mode (real-time speech)"
echo ""

read -p "Press Enter to start the demo..."

echo ""
echo "🔇 DEMO 1: Text-only mode (no audio)"
echo "====================================="
echo "Running a quick debate with text output only..."
echo ""

./start_debate.sh --topic "Should we trust AI?" --rounds 1

echo ""
echo "Press Enter to continue to voice mode..."
read

echo ""
echo "🔊 DEMO 2: Voice synthesis mode (real-time speech)"
echo "=================================================="
echo "Running the same debate with real-time voice synthesis..."
echo "You'll hear different voices for each character!"
echo ""

./start_debate.sh --topic "Should we trust AI?" --rounds 1 --audio

echo ""
echo "🎉 Demo complete!"
echo ""
echo "Key differences:"
echo "• Text-only: Fast, silent, saves text files"
echo "• Voice mode: Real-time speech, different voices per character, saves audio files"
echo ""
echo "Character voices:"
echo "• Truth Seeker: Ralph (deep, paranoid male)"
echo "• Skeptic: Samantha (clear, logical female)"
