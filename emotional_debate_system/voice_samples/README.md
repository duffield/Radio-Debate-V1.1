# Voice Samples for Chatterbox TTS

## 📁 Folder Structure

```
voice_samples/
├── debater_1/
│   ├── voice_sample.wav     # Primary voice sample (10-15 seconds)
│   ├── voice_sample.mp3     # MP3 files work too!
│   ├── voice_sample.m4a     # M4A also supported
│   └── metadata.txt         # Optional: Info about the speaker
├── debater_2/
│   ├── voice_sample.wav     # Primary voice sample (10-15 seconds)
│   ├── voice_sample.mp3     # MP3 files work too!
│   ├── voice_sample.m4a     # M4A also supported
│   └── metadata.txt
└── README.md               # This file
```

## 🎤 Voice Recording Guidelines

### For Best Chatterbox TTS Results:

1. **Duration**: 10-15 seconds is optimal
2. **Quality**: Clear, no background noise
3. **Content**: Natural speech, varied sentences
4. **Format**: WAV, MP3, or M4A files (all supported!)

### Recording Tips:

- **Speak clearly and naturally**
- **Use varied sentence structures**
- **Include some emotion/expression**
- **Avoid monotone delivery**
- **Record in a quiet environment**

### Example Recording Script:
```
"Hello, my name is [Name]. I enjoy discussing complex topics and sharing different perspectives. Technology fascinates me, especially how it impacts our daily lives and society."
```

## 🤖 How Chatterbox Uses These:

1. **Zero-shot cloning**: No training required
2. **Single sample**: Each debater needs just one good 10-15s sample
3. **Instant generation**: Voice cloning happens in real-time
4. **High quality**: Produces natural-sounding speech

## 📋 File Naming Convention:

- `voice_sample.wav` - Main sample for voice cloning
- `voice_sample_2.wav` - Optional backup/additional sample
- `metadata.txt` - Speaker info (optional)

## 🎭 Usage in Debate System:

```python
# The system will automatically use these files:
debater_1_voice = "voice_samples/debater_1/voice_sample.wav"
debater_2_voice = "voice_samples/debater_2/voice_sample.wav"

# Chatterbox will clone these voices for the debate
debate_agent_1 = ChatterboxAgent(debater_1_voice)
debate_agent_2 = ChatterboxAgent(debater_2_voice)
```