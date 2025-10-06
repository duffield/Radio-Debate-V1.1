import ollama
from typing import List
from .base import BaseLLM, DebateResponse, EmotionMetadata

class OllamaLLM(BaseLLM):
    """Local Ollama LLM provider"""
    
    def __init__(self, model: str = "llama3.1:8b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.client = ollama.Client(host=host)
    
    def generate_with_emotion(self, prompt: str, character: str = "skeptical") -> DebateResponse:
        """Generate debate response with emotion inference"""
        
        system_prompt = self._get_character_prompt(character)
        
        # Generate response
        response = self.client.chat(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            options={
                'temperature': 0.7,
                'num_predict': 150,
            }
        )
        
        text = response['message']['content'].strip()
        
        # Infer basic emotions from text
        emotions = self._infer_basic_emotions(text)
        
        return DebateResponse(
            text=text,
            emotions=emotions,
            primary_emotion=emotions[0].name if emotions else "neutral",
            valence=self._calculate_valence(text),
            arousal=self._calculate_arousal(text),
            metadata={'model': self.model, 'character': character}
        )
    
    def _get_character_prompt(self, character: str) -> str:
        """Get character-specific system prompt"""
        prompts = {
            "worried": """You are a TRUTH SEEKER investigating shapeshifting lizard people. 
            You are increasingly paranoid and see connections everywhere. Keep responses to 2-3 sentences.
            Express concern, suspicion, and urgency in your language.""",
            
            "skeptical": """You are a SKEPTIC who thinks conspiracy theories about lizard people are nonsense.
            You value evidence and logic. Keep responses to 2-3 sentences.
            Express frustration with unfounded claims and demand proof."""
        }
        return prompts.get(character, prompts["skeptical"])
    
    def _infer_basic_emotions(self, text: str) -> List[EmotionMetadata]:
        """Infer basic emotions from text using simple heuristics"""
        emotions = []
        text_lower = text.lower()
        
        # Simple emotion detection based on keywords
        emotion_keywords = {
            "worry": ["worry", "concern", "anxious", "nervous", "fear"],
            "anger": ["angry", "mad", "furious", "outrage", "rage"],
            "sadness": ["sad", "depressed", "disappointed", "grief"],
            "joy": ["happy", "joy", "excited", "thrilled", "delighted"],
            "surprise": ["surprised", "shocked", "amazed", "stunned"],
            "disgust": ["disgusted", "revolted", "sickened", "repulsed"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            intensity = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
            if intensity > 0:
                emotions.append(EmotionMetadata(
                    name=emotion,
                    intensity=min(intensity, 1.0),
                    confidence=0.8
                ))
        
        # Sort by intensity
        emotions.sort(key=lambda x: x.intensity, reverse=True)
        return emotions[:3]  # Return top 3
    
    def _calculate_valence(self, text: str) -> float:
        """Calculate valence (positive/negative) from text"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "enjoy"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "horrible", "worst", "disgusting"]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total
    
    def _calculate_arousal(self, text: str) -> float:
        """Calculate arousal (calm/excited) from text"""
        high_arousal_words = ["!", "excited", "urgent", "immediately", "now", "quickly", "fast", "rush"]
        text_lower = text.lower()
        
        arousal_score = sum(1 for word in high_arousal_words if word in text_lower)
        arousal_score += text.count("!") * 0.5  # Exclamation marks
        
        return min(arousal_score / 5.0, 1.0)  # Normalize to 0-1
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            self.client.list()
            return True
        except Exception:
            return False
