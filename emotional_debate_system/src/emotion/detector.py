from transformers import pipeline
import torch
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from llm.base import DebateResponse, EmotionMetadata

class EmotionDetector:
    """Emotion detection using transformers"""
    
    def __init__(self, model: str = "SamLowe/roberta-base-go_emotions", device: str = "cpu"):
        self.model_name = model
        
        # Determine device
        if device == "mps" and torch.backends.mps.is_available():
            self.device = "mps"
            print("🎨 Using Metal Performance Shaders (M1 GPU)")
        elif device == "cuda" and torch.cuda.is_available():
            self.device = 0
            print("🎮 Using CUDA GPU")
        else:
            self.device = -1
            print("🖥️  Using CPU")
        
        print(f"Loading emotion model: {model}...")
        self.classifier = pipeline(
            "text-classification",
            model=model,
            top_k=None,
            device=self.device
        )
        print("✅ Emotion detector ready!")
    
    def enrich_emotions(self, debate_response: DebateResponse, threshold: float = 0.3) -> DebateResponse:
        """Enrich debate response with detected emotions"""
        
        # Detect emotions from text
        results = self.classifier(debate_response.text)[0]
        
        # Filter significant emotions
        significant_emotions = [
            EmotionMetadata(
                name=emotion['label'],
                intensity=emotion['score'],
                confidence=1.0
            )
            for emotion in results
            if emotion['score'] > threshold
        ]
        
        # Sort by intensity
        significant_emotions.sort(key=lambda x: x.intensity, reverse=True)
        
        # Update debate response
        if significant_emotions:
            debate_response.emotions = significant_emotions
            debate_response.primary_emotion = significant_emotions[0].name
            debate_response.valence = self._calculate_valence_from_emotions(significant_emotions)
            debate_response.arousal = self._calculate_arousal_from_emotions(significant_emotions)
        
        return debate_response
    
    def _calculate_valence_from_emotions(self, emotions: List[EmotionMetadata]) -> float:
        """Calculate valence from detected emotions"""
        positive_emotions = {'joy', 'amusement', 'excitement', 'gratitude', 'love', 
                           'optimism', 'caring', 'admiration', 'approval', 'pride', 'relief'}
        negative_emotions = {'anger', 'annoyance', 'disappointment', 'sadness', 
                           'fear', 'nervousness', 'disgust', 'grief', 'remorse'}
        
        pos_score = sum(e.intensity for e in emotions if e.name in positive_emotions)
        neg_score = sum(e.intensity for e in emotions if e.name in negative_emotions)
        
        total = pos_score + neg_score
        if total == 0:
            return 0.0
        
        return (pos_score - neg_score) / total
    
    def _calculate_arousal_from_emotions(self, emotions: List[EmotionMetadata]) -> float:
        """Calculate arousal from detected emotions"""
        high_arousal = {'excitement', 'anger', 'fear', 'surprise', 'nervousness', 'amusement'}
        
        arousal_score = sum(e.intensity for e in emotions if e.name in high_arousal)
        total_score = sum(e.intensity for e in emotions)
        
        if total_score == 0:
            return 0.0
        
        return arousal_score / total_score