#!/bin/bash

# Emotional AI Debate System Launcher
# A user-friendly script to start the debate system

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_TOPIC="Should we worry about shapeshifting lizard people controlling world governments?"
DEFAULT_ROUNDS=3
DEFAULT_AUDIO="--no-audio"

# Function to show usage
show_usage() {
    echo -e "${CYAN}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -t, --topic TOPIC     Debate topic (default: '$DEFAULT_TOPIC')"
    echo "  -r, --rounds NUM      Number of debate rounds (default: $DEFAULT_ROUNDS)"
    echo "  -a, --audio           Enable audio synthesis (default: disabled)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0                                    # Run with defaults"
    echo "  $0 -t 'AI will replace humans' -r 5  # Custom topic and rounds"
    echo "  $0 --audio                           # Enable audio synthesis"
    echo "  $0 -t 'Climate change' -r 2 -a       # All options"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Virtual environment not found${NC}"
        echo -e "${YELLOW}   Run: ./setup.sh${NC}"
        exit 1
    fi
    
    # Check if main.py exists
    if [ ! -f "src/main.py" ]; then
        echo -e "${RED}❌ Main application not found${NC}"
        echo -e "${YELLOW}   Run: ./setup.sh${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to start Ollama if needed
start_ollama() {
    echo -e "${BLUE}🤖 Checking Ollama...${NC}"
    
    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is already running${NC}"
        return 0
    fi
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        echo -e "${YELLOW}⚠️  Ollama not found in PATH${NC}"
        echo -e "${YELLOW}   The system will run in limited mode (no LLM responses)${NC}"
        return 1
    fi
    
    # Start Ollama
    echo -e "${YELLOW}🚀 Starting Ollama server...${NC}"
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Wait for Ollama to be ready
    echo -e "${YELLOW}⏳ Waiting for Ollama to be ready...${NC}"
    sleep 3
    
    # Check if Ollama started successfully
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama server started (PID: $OLLAMA_PID)${NC}"
        echo $OLLAMA_PID > .ollama_pid
        return 0
    else
        echo -e "${RED}❌ Ollama server failed to start${NC}"
        kill $OLLAMA_PID 2>/dev/null
        return 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Cleaning up...${NC}"
    
    # Stop Ollama if we started it
    if [ -f .ollama_pid ]; then
        OLLAMA_PID=$(cat .ollama_pid)
        if kill -0 $OLLAMA_PID 2>/dev/null; then
            echo -e "${YELLOW}   Stopping Ollama server...${NC}"
            kill $OLLAMA_PID 2>/dev/null
            echo -e "${GREEN}✅ Ollama server stopped${NC}"
        fi
        rm -f .ollama_pid
    fi
    
    # Deactivate virtual environment
    if [ ! -z "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Parse command line arguments
TOPIC="$DEFAULT_TOPIC"
ROUNDS="$DEFAULT_ROUNDS"
AUDIO_FLAG="$DEFAULT_AUDIO"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--topic)
            TOPIC="$2"
            shift 2
            ;;
        -r|--rounds)
            ROUNDS="$2"
            shift 2
            ;;
        -a|--audio)
            AUDIO_FLAG=""
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
echo -e "${GREEN}🦎 Emotional AI Debate System${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Check prerequisites
check_prerequisites

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Start Ollama (optional)
start_ollama
OLLAMA_AVAILABLE=$?

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Display configuration
echo ""
echo -e "${CYAN}📋 Configuration:${NC}"
echo -e "   Topic: ${YELLOW}$TOPIC${NC}"
echo -e "   Rounds: ${YELLOW}$ROUNDS${NC}"
echo -e "   Audio: ${YELLOW}$([ -n "$AUDIO_FLAG" ] && echo "Disabled" || echo "Enabled")${NC}"
echo -e "   Ollama: ${YELLOW}$([ $OLLAMA_AVAILABLE -eq 0 ] && echo "Available" || echo "Not available")${NC}"
echo ""

# Run the debate
echo -e "${GREEN}🎭 Starting debate...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

if [ -n "$AUDIO_FLAG" ]; then
    python src/main.py --topic "$TOPIC" --rounds "$ROUNDS" $AUDIO_FLAG
else
    python src/main.py --topic "$TOPIC" --rounds "$ROUNDS"
fi

# Cleanup
cleanup
