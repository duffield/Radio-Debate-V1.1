# Emotional Debate System - Chatterbox TTS Edition

## M1 Max Optimized Voice Cloning for Art Installations

This project has been redesigned to use **Chatterbox TTS** with M1 Max optimization for real-time voice cloning in art installations. The system explores themes of identity and artificial intelligence through emotional debates using the visitor's own voice.

## 🚀 Quick Start

### 1. Setup M1 Optimized Environment

```bash
# Run the automated setup script
./setup_m1_chatterbox.sh
```

This will:
- Create a conda environment: `voice_m1_chatterbox`
- Install PyTorch with MPS support
- Install Chatterbox TTS and dependencies
- Verify MPS is working correctly

### 2. Verify Installation

```bash
# Activate the environment
conda activate voice_m1_chatterbox

# Verify setup
python verify_m1_setup.py
```

### 3. Run Art Installation

```bash
# Full interactive installation workflow
python art_installation_workflow.py

# Or test the voice agent directly
python m1_optimized_voice.py
```

## 📁 Project Structure

```
emotional_debate_system/
├── setup_m1_chatterbox.sh          # Automated M1 setup script
├── activate_m1_chatterbox.sh       # Quick activation script  
├── verify_m1_setup.py              # Installation verification
├── m1_optimized_voice.py           # Core M1 optimized voice agent
├── art_installation_workflow.py    # Complete installation workflow
├── requirements_m1_chatterbox.txt  # M1 optimized requirements
├── README_CHATTERBOX.md           # This file
├── .gitignore                      # Updated with voice file patterns
├── src/                           # Legacy modules (deprecated)
└── config/                        # Legacy config (deprecated)
```

## 🎭 Art Installation Workflow

The installation follows this workflow:

1. **Voice Recording** (15 seconds)
   - Visitor records voice sample
   - Instructions provided for optimal results

2. **Voice Cloning Setup** (~5-10 seconds)
   - Initialize Chatterbox TTS with MPS acceleration
   - Load and warm up the model

3. **Debate Preparation** (~30-60 seconds)
   - Pre-generate all debate statements
   - Cache audio for instant playback

4. **Emotional Debate** (Instant playback)
   - Play philosophical dialogue in visitor's voice
   - Explores themes of identity and AI

5. **Cleanup** (Immediate)
   - Remove all visitor voice data
   - Clear memory caches

## ⚡ Performance Optimization Strategies

### Strategy 1: Sentence Chunking (Real-time Feel)
```python
# Split long sentences into 5-10 word chunks
agent.speak_chunked(long_text, chunk_size=6)
# Result: 200ms to first audio instead of 500ms
```

### Strategy 2: Pre-generation (Art Installation)
```python
# Generate all audio at startup
cached_audio = agent.pre_generate_statements(statements)
# Result: Instant playback during visitor interaction
```

### Strategy 3: Parallel Generation + Playback
```python
# Generate next while playing current
agent.speak_with_parallel_generation(statements)
# Result: Seamless flow between statements
```

## 📊 Expected Performance (M1 Max)

- **Short sentences** (5-8 words): ~200-300ms generation
- **Medium sentences** (10-15 words): ~400-500ms generation  
- **Long sentences** (20+ words): ~800ms-1.2s generation

**Optimization Result:**
- Pre-generation setup: ~25 seconds (acceptable for installation)
- Debate playback: **Instant** (no generation delays)

## 🔧 Technical Details

### M1 Max Optimizations
- **MPS Acceleration**: PyTorch with Metal Performance Shaders
- **Memory Management**: Automatic MPS cache clearing
- **Multi-threading**: Optimized for M1 Max 10-core CPU
- **Audio Settings**: Buffer optimization for real-time playback

### Dependencies
- **PyTorch 2.0+** with MPS support
- **Chatterbox TTS** for voice cloning
- **sounddevice/soundfile** for audio I/O
- **psutil** for performance monitoring

## 🎯 Usage Examples

### Basic Voice Cloning
```python
from m1_optimized_voice import M1OptimizedVoiceAgent

agent = M1OptimizedVoiceAgent("voice_sample.wav")
agent.initialize_model()
agent.speak("Hello, this is your voice speaking!")
```

### Installation Mode
```python
from art_installation_workflow import ArtInstallationWorkflow

workflow = ArtInstallationWorkflow()
workflow.run_full_workflow(visitor_name="Artist")
```

### Performance Benchmarking
```python
agent = M1OptimizedVoiceAgent("voice_sample.wav")
agent.initialize_model()
results = agent.benchmark_performance()
print(f"Average generation time: {results['average_time']:.3f}s")
```

## 🔍 Troubleshooting

### MPS Not Available
```bash
# Check macOS version (requires 12.3+)
sw_vers

# Reinstall PyTorch with MPS
pip uninstall torch torchvision torchaudio
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Slow Performance (>1s per sentence)
1. **Check device**: Ensure using 'mps', not 'cpu'
2. **Close other apps**: Chrome and heavy applications
3. **Monitor thermal**: Check Activity Monitor for thermal pressure
4. **Use chunking**: Break long sentences into smaller parts

### Audio Glitches/Crackling
```python
# Increase buffer size
import sounddevice as sd
sd.default.blocksize = 2048
sd.default.latency = 'high'
```

## 🛠️ Development

### Adding New Debate Content
Edit `art_installation_workflow.py`:
```python
self.debate_statements = [
    "Your custom debate statement here...",
    # Add more statements
]
```

### Performance Monitoring
```python
# Track memory usage
agent.print_memory_usage()

# Get performance summary
summary = agent.get_performance_summary()
```

### Custom Voice Samples
Place audio files in project root:
- `voice_sample.wav` (default test sample)
- `test_voice.wav` (alternative test sample)

## 📝 License & Ethics

This project is designed for educational and artistic purposes. When using in installations:

1. **Consent**: Always obtain explicit consent for voice recording
2. **Privacy**: Automatically delete voice data after each session
3. **Transparency**: Inform visitors about the voice cloning process
4. **Responsibility**: Use ethically and avoid deceptive applications

## 🎨 Art Installation Tips

### Setup Recommendations
- **Hardware**: M1 Max MacBook with 32GB+ RAM
- **Audio**: Quality microphone for voice recording
- **Display**: Large screen for instructions/visualization
- **Space**: Quiet environment for voice recording

### Visitor Experience
- **Recording**: 15 seconds is optimal (enough for cloning, not too long)
- **Wait Time**: ~25 seconds preparation is acceptable for art context
- **Playback**: Pre-generated audio ensures smooth experience
- **Privacy**: Emphasize that voice data is immediately deleted

## 🚀 Future Enhancements

- [ ] Real-time voice morphing during conversation
- [ ] Multiple voice personality modes
- [ ] Integration with emotion recognition
- [ ] Multi-language support
- [ ] Advanced audio effects and processing
- [ ] Web-based interface for remote installations

---

**For technical support or artistic collaboration opportunities, please contact the development team.**