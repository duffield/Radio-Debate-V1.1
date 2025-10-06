#!/bin/bash

echo "📡 Creating OSC streaming module..."

cat > src/streaming/osc_streamer.py << 'EOF'
from pythonosc import udp_client
import time
from typing import Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from llm.base import DebateResponse

class OSCStreamer:
    """Stream emotion data via OSC to TouchDesigner"""
    
    def __init__(self, ip: str = "127.0.0.1", port: int = 5005, fps: int = 30):
        self.client = udp_client.SimpleUDPClient(ip, port)
        self.fps = fps
        self.frame_time = 1.0 / fps
        print(f"📡 OSC streaming to {ip}:{port} @ {fps} FPS")
    
    def stream_debate_response(self, debate_response: DebateResponse, agent_name: str = "agent"):
        """Stream all emotion parameters"""
        
        # Stream primary emotions (top 5)
        for emotion in debate_response.emotions[:5]:
            address = f"/{agent_name}/emotion/{emotion.name}"
            self.client.send_message(address, float(emotion.intensity))
        
        # Stream dimensional values
        self.client.send_message(f"/{agent_name}/valence", float(debate_response.valence))
        self.client.send_message(f"/{agent_name}/arousal", float(debate_response.arousal))
        
        # Stream metadata
        self.client.send_message(f"/{agent_name}/primary_emotion", debate_response.primary_emotion)
        
        if hasattr(self, 'debug') and self.debug:
            print(f"  📤 Streamed to /{agent_name}/* via OSC")
    
    def stream_continuous(self, emotion_dict: Dict[str, float], agent_name: str = "agent"):
        """Stream emotion updates at consistent FPS"""
        start_time = time.time()
        
        for key, value in emotion_dict.items():
            self.client.send_message(f"/{agent_name}/{key}", float(value))
        
        # Maintain timing
        elapsed = time.time() - start_time
        if elapsed < self.frame_time:
            time.sleep(self.frame_time - elapsed)
EOF

echo "✅ Created src/streaming/osc_streamer.py"
echo ""
echo "🎉 OSC streaming module complete!"