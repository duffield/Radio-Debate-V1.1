#!/bin/bash

# Debate Launcher Script
# This script starts the Ollama server and runs the Python vs JS debate

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 Starting AI Debate System${NC}"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama not found. Please run ./setup.sh first${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run ./setup.sh first${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Start Ollama server in background
echo -e "${YELLOW}🚀 Starting Ollama server...${NC}"
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo -e "${YELLOW}⏳ Waiting for Ollama to be ready...${NC}"
sleep 3

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${RED}❌ Ollama server failed to start${NC}"
    kill $OLLAMA_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Ollama server running (PID: $OLLAMA_PID)${NC}"
echo ""
echo -e "${GREEN}🗣️  Starting the eternal Python vs JavaScript debate...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the debate${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping debate...${NC}"
    kill $OLLAMA_PID 2>/dev/null
    echo -e "${GREEN}✅ Ollama server stopped${NC}"
    deactivate
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Add project root to Python path and run the debate
PYTHONPATH="${PYTHONPATH}:$(pwd)" python src/main.py

# Cleanup if script ends normally
cleanup