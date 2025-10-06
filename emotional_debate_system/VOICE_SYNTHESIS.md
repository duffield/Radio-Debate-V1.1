# 🔊 Voice Synthesis Guide

This guide explains how to enable and use voice synthesis in the Emotional AI Debate System.

## 🎯 Quick Start

### Enable Voice Synthesis
```bash
# Using the full launcher
./start_debate.sh --topic "Your topic" --rounds 3 --audio

# Using the simple launcher
./run.sh --topic "Your topic" --rounds 3 --audio

# Using Python directly
python src/main.py --topic "Your topic" --rounds 3 --audio
```

### Disable Voice Synthesis (Default)
```bash
# No audio (default behavior)
./start_debate.sh --topic "Your topic" --rounds 3

# Explicitly disable
./start_debate.sh --topic "Your topic" --rounds 3 --no-audio
```

## 🎤 Voice Synthesis Options

### Option 1: macOS System TTS (Recommended)
**Status**: ✅ Working
- Uses macOS built-in `say` command
- High quality voices
- No additional installation required
- Default voice: Samantha

**Available Voices**:
- Samantha (default) - Clear American English
- Alex - Male American English  
- Victoria - Female American English
- Daniel - British English
- And many more...

**To change voice**:
Edit `src/tts/macos_provider.py` and change the default voice:
```python
def __init__(self, voice: str = "Samantha"):  # Change this
```

### Option 2: Coqui TTS (Advanced)
**Status**: ⚠️ Requires Python 3.11
- Higher quality synthesis
- More voice options
- Requires separate setup

**Setup**:
```bash
./setup_tts.sh  # Creates Python 3.11 environment
source venv_tts/bin/activate
python src/main.py --audio
```

### Option 3: Text-Only Mode (Fallback)
**Status**: ✅ Always Available
- Saves text files instead of audio
- No voice synthesis
- Works on any system

## 📁 Output Files

### Audio Files (when --audio enabled)
- **Format**: AIFF (.aiff)
- **Location**: `data/audio_output/`
- **Naming**: `debate_{timestamp}.aiff`
- **Size**: ~300-600KB per response

### Text Files (fallback or --no-audio)
- **Format**: Text (.txt)
- **Location**: `data/audio_output/`
- **Content**: Response text + emotion data

## 🎛️ Voice Customization

### Change Default Voice
1. Edit `src/tts/macos_provider.py`
2. Change the voice parameter:
```python
def __init__(self, voice: str = "Samantha"):  # Change to desired voice
```

### List Available Voices
```bash
say -v "?" | grep "en_US"  # English voices
say -v "?" | grep "en_GB"  # British voices
```

### Popular Voice Options
- **Samantha** - Clear, professional female
- **Alex** - Deep, authoritative male
- **Victoria** - Warm, friendly female
- **Daniel** - British accent male
- **Kathy** - Older, wise female

## 🔧 Troubleshooting

### "Voice not found" Error
- Check available voices: `say -v "?"`
- Update voice name in `macos_provider.py`
- Use exact voice name (case-sensitive)

### "TTS not available" Error
- macOS `say` command not found
- System will fallback to text-only mode
- Check macOS accessibility permissions

### Audio Files Not Playing
- AIFF format requires compatible player
- Try VLC, QuickTime, or convert to MP3
- Check file permissions in `data/audio_output/`

### Performance Issues
- Voice synthesis takes 2-5 seconds per response
- Consider using `--no-audio` for faster testing
- Longer responses take more time to synthesize

## 📊 Performance Comparison

| Method | Quality | Speed | Setup | Compatibility |
|--------|---------|-------|-------|---------------|
| macOS TTS | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | macOS only |
| Coqui TTS | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Cross-platform |
| Text-only | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | All systems |

## 🎵 Audio Playback

### Play Generated Audio
```bash
# Play a specific file
afplay data/audio_output/debate_1234567890.aiff

# Play all audio files
for file in data/audio_output/*.aiff; do
    echo "Playing: $file"
    afplay "$file"
done
```

### Convert to MP3 (Optional)
```bash
# Install ffmpeg first: brew install ffmpeg
ffmpeg -i debate_1234567890.aiff debate_1234567890.mp3
```

## 🎭 Character Voices

The system currently uses the same voice for both characters. To differentiate:

1. **Modify the TTS provider** to accept character-specific voices
2. **Update main.py** to pass character information
3. **Use different voices** for Truth Seeker vs Skeptic

Example character voice mapping:
- Truth Seeker: "Alex" (paranoid, deep)
- Skeptic: "Samantha" (logical, clear)

## 📝 Notes

- Audio files are generated in real-time during debates
- Each response creates a separate audio file
- Files are automatically saved to `data/audio_output/`
- The system gracefully falls back to text-only if TTS fails
- Voice synthesis adds 2-5 seconds per response
