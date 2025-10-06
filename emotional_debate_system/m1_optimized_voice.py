"""
M1 Max Optimized Voice Agent using Chatterbox TTS
Designed for real-time voice cloning and debate generation
"""

import os
import time
import threading
import queue
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import warnings

import torch
import numpy as np
import sounddevice as sd
import soundfile as sf
import psutil
from chatterbox.tts import ChatterboxTTS

warnings.filterwarnings("ignore", category=UserWarning)


class M1OptimizedVoiceAgent:
    """
    M1 Max optimized voice agent with multiple performance strategies:
    1. Sentence chunking for real-time feel
    2. Pre-generation for instant playback
    3. Parallel generation + playback
    
    Supports multiple voices for debate scenarios
    """

    def __init__(self, voice_sample_path: Optional[str] = None, device: str = "auto", debater_name: str = "Debater"):
        self.voice_sample_path = voice_sample_path
        self.debater_name = debater_name
        self.device = self._get_optimal_device(device)
        self.model = None
        self.audio_cache: Dict[str, np.ndarray] = {}
        self.generation_queue = queue.Queue()
        
        # Audio settings optimized for M1 Max
        self._setup_audio_settings()
        
        # Performance tracking
        self.generation_times = []
        self.memory_usage = []
        
        print(f"🚀 M1OptimizedVoiceAgent initialized for {debater_name}")
        print(f"   Device: {self.device}")
        print(f"   Voice sample: {voice_sample_path}")

    def _get_optimal_device(self, device: str) -> str:
        """Determine the best device for M1 Max"""
        if device == "auto":
            if torch.backends.mps.is_available() and torch.backends.mps.is_built():
                return "mps"
            else:
                print("⚠️  MPS not available, falling back to CPU")
                return "cpu"
        return device

    def _setup_audio_settings(self):
        """Optimize audio settings for M1 Max"""
        # Increase buffer size to prevent crackling
        sd.default.blocksize = 2048
        sd.default.latency = 'high'
        sd.default.channels = 1
        sd.default.samplerate = 22050
        
        # Set environment variables for optimal performance
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        os.environ['OMP_NUM_THREADS'] = '8'  # M1 Max has 10 cores, leave 2 for system
        os.environ['MKL_NUM_THREADS'] = '8'

    def initialize_model(self) -> bool:
        """Initialize Chatterbox TTS model with M1 optimization"""
        try:
            print("🔄 Loading Chatterbox TTS model...")
            start_time = time.time()
            
            self.model = ChatterboxTTS.from_pretrained(device=self.device)
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.2f}s on {self.device}")
            
            # Warm up model with a test generation
            if self.voice_sample_path and os.path.exists(self.voice_sample_path):
                print("🔥 Warming up model...")
                self._warmup_model()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize model: {e}")
            return False

    def _warmup_model(self):
        """Warm up the model for better performance"""
        try:
            warmup_text = "Testing voice cloning."
            start_time = time.time()
            
            _ = self.model.generate(
                warmup_text,
                audio_prompt_path=self.voice_sample_path,
                temperature=0.6,
                exaggeration=0.0,
            )
            
            warmup_time = time.time() - start_time
            print(f"🔥 Model warmed up in {warmup_time:.2f}s")
            
        except Exception as e:
            print(f"⚠️  Warmup failed (this is normal): {e}")

    def generate_audio(self, text: str, voice_sample: Optional[str] = None) -> np.ndarray:
        """Generate audio using Chatterbox TTS with performance optimization"""
        if not self.model:
            raise RuntimeError("Model not initialized. Call initialize_model() first.")
        
        voice_path = voice_sample or self.voice_sample_path
        if not voice_path or not os.path.exists(voice_path):
            raise ValueError(f"Voice sample not found: {voice_path}")
        
        start_time = time.time()
        
        try:
            # Generate audio with optimal settings for speed
            audio_tensor = self.model.generate(
                text,
                audio_prompt_path=voice_path,
                temperature=0.6,      # Slightly lower for speed
                exaggeration=0.0,     # Neutral is fastest
            )
            
            # Convert to numpy array if needed
            if isinstance(audio_tensor, torch.Tensor):
                audio_array = audio_tensor.cpu().numpy()
            else:
                audio_array = audio_tensor
            
            generation_time = time.time() - start_time
            self.generation_times.append(generation_time)
            
            print(f"⚡ Generated '{text[:30]}...' in {generation_time:.3f}s")
            
            return audio_array
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            raise

    def play_audio(self, audio_array: np.ndarray, wait: bool = True):
        """Play audio with optimized settings"""
        try:
            sd.play(audio_array, samplerate=22050)
            if wait:
                sd.wait()
        except Exception as e:
            print(f"❌ Playback failed: {e}")

    def speak(self, text: str, voice_sample: Optional[str] = None, wait: bool = True):
        """Generate and play speech"""
        audio = self.generate_audio(text, voice_sample)
        self.play_audio(audio, wait)

    # Strategy 1: Sentence Chunking
    def speak_chunked(self, text: str, voice_sample: Optional[str] = None, 
                      chunk_size: int = 8) -> float:
        """
        Split text into chunks for faster perceived response time
        Returns total time for first chunk (perceived latency)
        """
        words = text.split()
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        
        print(f"📝 Speaking in {len(chunks)} chunks of ~{chunk_size} words")
        
        first_chunk_time = None
        
        for i, chunk in enumerate(chunks):
            start_time = time.time()
            audio = self.generate_audio(chunk, voice_sample)
            
            if i == 0:
                first_chunk_time = time.time() - start_time
                print(f"⚡ First chunk ready in {first_chunk_time:.3f}s (perceived latency)")
            
            self.play_audio(audio, wait=True)
        
        return first_chunk_time

    # Strategy 2: Pre-generation
    def pre_generate_statements(self, statements: List[str], 
                               voice_sample: Optional[str] = None) -> Dict[str, np.ndarray]:
        """Pre-generate all audio for instant playback during installation"""
        print(f"🎯 Pre-generating {len(statements)} statements...")
        
        start_time = time.time()
        cached_audio = {}
        
        for i, statement in enumerate(statements, 1):
            print(f"Generating {i}/{len(statements)}: '{statement[:40]}...'")
            
            try:
                audio = self.generate_audio(statement, voice_sample)
                cached_audio[statement] = audio
                
                # Clear MPS cache to prevent memory buildup
                if self.device == "mps":
                    torch.mps.empty_cache()
                    
            except Exception as e:
                print(f"⚠️  Failed to generate statement {i}: {e}")
                continue
        
        total_time = time.time() - start_time
        print(f"✅ Pre-generation complete in {total_time:.2f}s")
        print(f"   {len(cached_audio)} statements ready for instant playback")
        
        self.audio_cache.update(cached_audio)
        return cached_audio

    def play_cached_statement(self, statement: str) -> bool:
        """Play pre-generated audio instantly"""
        if statement in self.audio_cache:
            self.play_audio(self.audio_cache[statement], wait=False)
            return True
        else:
            print(f"⚠️  Statement not in cache: '{statement[:40]}...'")
            return False

    # Strategy 3: Parallel Generation + Playback
    def speak_with_parallel_generation(self, statements: List[str], 
                                     voice_sample: Optional[str] = None):
        """Generate next statement while playing current one"""
        if not statements:
            return
        
        print(f"🔄 Speaking {len(statements)} statements with parallel generation")
        
        # Generate first statement
        current_audio = self.generate_audio(statements[0], voice_sample)
        
        for i in range(len(statements)):
            # Start generating next statement in background (if exists)
            next_audio = None
            if i + 1 < len(statements):
                def generate_next():
                    nonlocal next_audio
                    next_audio = self.generate_audio(statements[i + 1], voice_sample)
                
                gen_thread = threading.Thread(target=generate_next)
                gen_thread.start()
            
            # Play current statement
            print(f"🔊 Playing statement {i + 1}: '{statements[i][:40]}...'")
            self.play_audio(current_audio, wait=True)
            
            # Wait for next generation to complete (if exists)
            if i + 1 < len(statements):
                gen_thread.join()
                current_audio = next_audio

    def benchmark_performance(self, test_statements: Optional[List[str]] = None) -> Dict[str, float]:
        """Benchmark generation performance on M1 Max"""
        if not self.model:
            raise RuntimeError("Model not initialized")
        
        if not test_statements:
            test_statements = [
                "This is a short test sentence.",
                "Here we have a medium length sentence for testing performance.",
                "This is a much longer sentence that contains many more words and should take longer to generate, testing the performance characteristics of the M1 Max processor with Chatterbox TTS."
            ]
        
        print("🏃 Benchmarking M1 Max performance...")
        
        results = {
            'short_sentence': [],
            'medium_sentence': [],
            'long_sentence': []
        }
        
        categories = ['short_sentence', 'medium_sentence', 'long_sentence']
        
        # Run each test 3 times
        for run in range(3):
            print(f"\n🔄 Benchmark Run {run + 1}/3")
            
            for i, statement in enumerate(test_statements):
                category = categories[i]
                start_time = time.time()
                
                try:
                    _ = self.generate_audio(statement, self.voice_sample_path)
                    generation_time = time.time() - start_time
                    results[category].append(generation_time)
                    
                    print(f"   {category}: {generation_time:.3f}s")
                    
                    # Clear cache between runs
                    if self.device == "mps":
                        torch.mps.empty_cache()
                        
                except Exception as e:
                    print(f"   ❌ {category} failed: {e}")
        
        # Calculate averages
        averages = {}
        for category, times in results.items():
            if times:
                avg = sum(times) / len(times)
                averages[category] = avg
                print(f"\n📊 {category} average: {avg:.3f}s")
        
        overall_avg = sum(averages.values()) / len(averages) if averages else 0
        print(f"\n🎯 Overall average: {overall_avg:.3f}s per generation")
        
        return averages

    def print_memory_usage(self):
        """Print current memory usage"""
        process = psutil.Process()
        mem_info = process.memory_info()
        mem_gb = mem_info.rss / 1024**3
        print(f"💾 Memory usage: {mem_gb:.2f} GB")
        self.memory_usage.append(mem_gb)

    def cleanup(self):
        """Clean up resources and clear caches"""
        print("🧹 Cleaning up resources...")
        
        if self.device == "mps":
            torch.mps.empty_cache()
        
        self.audio_cache.clear()
        
        # Clear queues
        while not self.generation_queue.empty():
            try:
                self.generation_queue.get_nowait()
            except queue.Empty:
                break
        
        print("✅ Cleanup complete")

    def get_performance_summary(self) -> Dict:
        """Get summary of performance metrics"""
        if not self.generation_times:
            return {"error": "No performance data available"}
        
        return {
            "total_generations": len(self.generation_times),
            "average_time": sum(self.generation_times) / len(self.generation_times),
            "min_time": min(self.generation_times),
            "max_time": max(self.generation_times),
            "memory_usage": {
                "current": self.memory_usage[-1] if self.memory_usage else 0,
                "peak": max(self.memory_usage) if self.memory_usage else 0,
                "average": sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
            }
        }


def main():
    """Demo the M1 optimized voice agent"""
    print("🎯 M1 Optimized Voice Agent Demo")
    
    # Initialize agent (replace with your voice sample path)
    voice_sample = "path/to/your/voice_sample.wav"  # Update this path
    agent = M1OptimizedVoiceAgent(voice_sample)
    
    if not agent.initialize_model():
        print("❌ Failed to initialize model")
        return
    
    # Test statements
    test_statements = [
        "Welcome to the emotional debate installation.",
        "I will speak with your voice now.",
        "What does identity mean in the age of artificial intelligence?",
        "Can a machine truly understand human emotion?",
        "Thank you for participating in this experience."
    ]
    
    print("\n" + "="*50)
    print("Strategy 1: Chunked Speech (Real-time Feel)")
    print("="*50)
    
    long_text = "This is a demonstration of chunked speech generation where we split long sentences into smaller chunks to provide faster perceived response times and better user experience."
    agent.speak_chunked(long_text, chunk_size=6)
    
    print("\n" + "="*50)
    print("Strategy 2: Pre-generation (Installation Mode)")
    print("="*50)
    
    # Pre-generate all statements
    cached_audio = agent.pre_generate_statements(test_statements[:3])
    
    # Play instantly
    print("🚀 Playing pre-generated audio instantly:")
    for statement in test_statements[:3]:
        print(f"Playing: '{statement[:40]}...'")
        agent.play_cached_statement(statement)
        time.sleep(1)  # Brief pause between statements
    
    print("\n" + "="*50)
    print("Strategy 3: Parallel Generation")
    print("="*50)
    
    agent.speak_with_parallel_generation(test_statements[-2:])
    
    print("\n" + "="*50)
    print("Performance Benchmark")
    print("="*50)
    
    agent.benchmark_performance()
    
    # Print summary
    summary = agent.get_performance_summary()
    print(f"\n📊 Performance Summary:")
    print(f"   Total generations: {summary['total_generations']}")
    print(f"   Average time: {summary['average_time']:.3f}s")
    print(f"   Range: {summary['min_time']:.3f}s - {summary['max_time']:.3f}s")
    
    agent.cleanup()
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()