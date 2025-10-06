# 🎭 Voice Cloning Setup Guide

## Quick Answer: Where to Put Voice Recordings

Put your voice recordings here:

```
voice_samples/
├── debater_1/
│   └── voice_sample.wav    # First person's voice (10-15 seconds)
└── debater_2/
│   └── voice_sample.wav    # Second person's voice (10-15 seconds)
```

## 🎤 Recording Your Voice Samples

### Step 1: Record Two Different Voices

You need **TWO different people** to record voice samples:

**Debater 1 Sample Script:**
> "Hello, I'm excited to participate in this debate about artificial intelligence and its impact on society. Technology has always fascinated me, and I believe we're on the cusp of remarkable breakthroughs."

**Debater 2 Sample Script:**  
> "Hi there, I'm looking forward to this discussion about AI. While technology offers great opportunities, I think we need to carefully consider the challenges and potential risks involved."

### Step 2: Recording Requirements

- **Duration**: 10-15 seconds each
- **Quality**: Clear, no background noise  
- **Format**: WAV files (preferred)
- **Sample rate**: 22050 Hz (or will be converted)
- **Content**: Natural speech, varied sentences

### Step 3: Save Files in Correct Location

```bash
# Create folders
mkdir -p voice_samples/debater_1 voice_samples/debater_2

# Save your recordings as:
voice_samples/debater_1/voice_sample.wav
voice_samples/debater_2/voice_sample.wav
```

## 🤖 How Chatterbox Uses These

Once you have both voice samples, Chatterbox will:

1. **Load the model** (takes ~10 seconds on M1 Max)
2. **Clone voices instantly** (no training needed!)
3. **Generate debate speech** using each cloned voice
4. **Play the debate** with both voices arguing

## 💡 Pro Tips

### For Better Voice Cloning:
- **Speak naturally** - don't read robotically
- **Include emotion** - vary your tone and pace
- **Use complete sentences** - helps the AI understand speech patterns
- **Record in quiet environment** - reduces noise interference

### Sample Quality Examples:
✅ **Good**: "Hello, I'm John. I love discussing technology and philosophy. What do you think about AI?"

❌ **Poor**: "Testing, testing, one, two, three, testing..." (too repetitive)

## 🚀 Next Steps

1. **Record your two voice samples** (10-15 seconds each)
2. **Save them in the correct folders** (see structure above)
3. **Run the voice cloning system**:
   ```bash
   conda activate voice_m1_chatterbox
   python two_debater_system.py  # (when I create this file)
   ```

## 📋 Troubleshooting

**Q: "I only have one voice - can I use the same person twice?"**  
A: You can, but the debate will sound like one person talking to themselves. Better to ask a friend/family member for the second voice sample.

**Q: "What if my voice sample is too short/long?"**  
A: 8-20 seconds usually works fine. Too short (<5s) may not have enough voice data. Too long (>30s) is unnecessary.

**Q: "Can I use MP3 files?"**  
A: WAV is preferred, but MP3 should work. The system will convert as needed.

**Q: "My voice sounds different when cloned"**  
A: This is normal with voice cloning. Try recording a clearer sample with more expression.

## 🎭 Example Debate Topics

Once your system is working, try these debate topics:

1. **AI and Creativity**: "Will AI enhance or replace human creativity?"
2. **Privacy vs Security**: "Should we sacrifice privacy for security?"
3. **Climate Solutions**: "Technology vs lifestyle changes for climate action?"
4. **Universal Basic Income**: "Is UBI the solution to automation?"
5. **Space Exploration**: "Mars colonization - necessity or luxury?"

Each debater will argue their side using the cloned voices!