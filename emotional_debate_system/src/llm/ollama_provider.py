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
