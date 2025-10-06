# 🦎 Emotional AI Debate System

An AI-powered debate system that generates emotional responses between two characters and streams data via OSC to TouchDesigner.

## 🚀 Quick Start

### Option 1: Quick Debate (Easiest)
```bash
./quick_debate.sh
```
This will prompt you for a topic and run a 3-round debate.

### Option 2: Full Control
```bash
./start_debate.sh --topic "Your debate topic" --rounds 5 --audio
```

### Option 3: Original Script
```bash
./run.sh --topic "Your topic" --rounds 3
```

## 📋 Available Scripts

| Script | Purpose | Features |
|--------|---------|----------|
| `quick_debate.sh` | Interactive quick start | Prompts for topic, 3 rounds, no audio |
| `start_debate.sh` | Full-featured launcher | All options, Ollama management, cleanup |
| `run.sh` | Simple launcher | Basic functionality, passes all args |

## 🎛️ Command Line Options

### start_debate.sh Options
- `-t, --topic TOPIC` - Debate topic (default: lizard people conspiracy)
- `-r, --rounds NUM` - Number of debate rounds (default: 3)
- `-a, --audio` - Enable audio synthesis (default: disabled)
- `-h, --help` - Show help message

### Examples
```bash
# Default debate
./start_debate.sh

# Custom topic and rounds
./start_debate.sh -t "Climate change is real" -r 5

# Enable audio synthesis
./start_debate.sh --audio

# All options
./start_debate.sh -t "AI ethics" -r 4 -a
```

## 🎭 How It Works

1. **Two AI Characters**: "Truth Seeker" (paranoid) vs "Skeptic" (logical)
2. **Emotion Detection**: Analyzes responses for emotional content
3. **OSC Streaming**: Sends data to TouchDesigner for visualization
4. **Text Output**: Saves debate transcripts to `data/audio_output/`

## 🔧 Prerequisites

- Python 3.13+ virtual environment
- Ollama (optional, for LLM responses)
- Dependencies installed via `pip install -r requirements.txt`

## 📁 Output

- **Console**: Real-time debate with emotion analysis
- **Files**: Text transcripts in `data/audio_output/`
- **OSC**: Emotion data streamed to `127.0.0.1:5005`

## 🛠️ Troubleshooting

- **"Virtual environment not found"** → Run `./setup.sh`
- **"Ollama not found"** → System runs in limited mode
- **"Main application not found"** → Run `./setup.sh`

## 🎨 TouchDesigner Integration

The system streams OSC data to TouchDesigner on port 5005:
- `/{agent}/emotion/{emotion_name}` - Emotion intensities
- `/{agent}/valence` - Positive/negative sentiment
- `/{agent}/arousal` - Calm/excited level
- `/{agent}/primary_emotion` - Main detected emotion

## 📝 Notes

- Audio synthesis is disabled by default (TTS package compatibility issues)
- System works without Ollama but with limited responses
- All scripts include proper cleanup on exit (Ctrl+C)
