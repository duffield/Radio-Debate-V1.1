#!/usr/bin/env python3
"""
M1 Max Setup Verification and Performance Testing
Verifies MPS support and benchmarks Chatterbox TTS performance
"""

import sys
import os
import time
from pathlib import Path
import subprocess
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_status(message: str, status: str = "info"):
    """Print status message with appropriate emoji"""
    emoji_map = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "loading": "🔄"
    }
    emoji = emoji_map.get(status, "ℹ️")
    print(f"{emoji} {message}")

def check_python_version():
    """Check Python version compatibility"""
    print_header("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print_status("Python version is compatible", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor} may not be optimal. Recommend Python 3.9+", "warning")
        return False

def check_conda_environment():
    """Check if running in correct conda environment"""
    print_header("Conda Environment Check")
    
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    print(f"Current environment: {conda_env}")
    
    if conda_env == "voice_m1_chatterbox":
        print_status("Running in correct conda environment", "success")
        return True
    else:
        print_status("Not in expected 'voice_m1_chatterbox' environment", "warning")
        print("  Run: conda activate voice_m1_chatterbox")
        return False

def check_pytorch_installation():
    """Check PyTorch installation and MPS support"""
    print_header("PyTorch Installation Check")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        print_status("PyTorch imported successfully", "success")
        
        # Check MPS availability
        mps_available = torch.backends.mps.is_available()
        mps_built = torch.backends.mps.is_built()
        
        print(f"MPS available: {mps_available}")
        print(f"MPS built: {mps_built}")
        
        if mps_available and mps_built:
            print_status("MPS is working correctly!", "success")
            
            # Test MPS tensor operations
            try:
                device = torch.device("mps")
                x = torch.randn(100, 100, device=device)
                y = torch.randn(100, 100, device=device)
                z = torch.mm(x, y)
                print_status("MPS tensor operations working", "success")
                return True
            except Exception as e:
                print_status(f"MPS tensor operations failed: {e}", "error")
                return False
        else:
            print_status("MPS not available", "error")
            print("  Possible fixes:")
            print("  1. Update to macOS 12.3 or later")
            print("  2. Reinstall PyTorch: pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu")
            return False
            
    except ImportError as e:
        print_status(f"PyTorch not installed: {e}", "error")
        return False

def check_chatterbox_installation():
    """Check Chatterbox TTS installation"""
    print_header("Chatterbox TTS Installation Check")
    
    try:
        from chatterbox.tts import ChatterboxTTS
        print_status("Chatterbox TTS imported successfully", "success")
        
        # Try to load model (this will download if not present)
        print_status("Attempting to load Chatterbox model...", "loading")
        
        try:
            model = ChatterboxTTS.from_pretrained(device="mps" if torch.backends.mps.is_available() else "cpu")
            print_status("Chatterbox model loaded successfully", "success")
            return True, model
        except Exception as e:
            print_status(f"Failed to load Chatterbox model: {e}", "error")
            return False, None
            
    except ImportError as e:
        print_status(f"Chatterbox TTS not installed: {e}", "error")
        print("  Install with: pip install chatterbox-tts")
        return False, None

def check_audio_dependencies():
    """Check audio processing dependencies"""
    print_header("Audio Dependencies Check")
    
    dependencies = [
        ("sounddevice", "sounddevice"),
        ("soundfile", "soundfile"),
        ("numpy", "numpy"),
        ("psutil", "psutil")
    ]
    
    all_good = True
    
    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print_status(f"{package_name} ✓", "success")
        except ImportError:
            print_status(f"{package_name} not found", "error")
            print(f"  Install with: pip install {package_name}")
            all_good = False
    
    return all_good

def benchmark_simple_generation(model):
    """Run a simple generation benchmark"""
    print_header("Simple Generation Benchmark")
    
    if not model:
        print_status("No model available for benchmarking", "error")
        return
    
    # Check if we have a sample audio file
    sample_files = [
        "voice_sample.wav",
        "test_voice.wav", 
        "sample.wav",
        "audio_sample.wav"
    ]
    
    voice_sample = None
    for sample in sample_files:
        if os.path.exists(sample):
            voice_sample = sample
            break
    
    if not voice_sample:
        print_status("No voice sample found for testing", "warning")
        print("  Create a short (~5-10s) audio file named 'voice_sample.wav' to test voice cloning")
        return
    
    print(f"Using voice sample: {voice_sample}")
    
    test_texts = [
        "This is a short test.",
        "Here is a medium length sentence for testing.",
        "This is a longer sentence that should take more time to generate and will help us understand the performance characteristics."
    ]
    
    results = []
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: '{text[:30]}...'")
        
        try:
            start_time = time.time()
            
            audio = model.generate(
                text,
                audio_prompt_path=voice_sample,
                temperature=0.6,
                exaggeration=0.0,
            )
            
            gen_time = time.time() - start_time
            results.append(gen_time)
            
            print_status(f"Generated in {gen_time:.3f}s", "success")
            
            # Clear cache
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
                
        except Exception as e:
            print_status(f"Generation failed: {e}", "error")
    
    if results:
        avg_time = sum(results) / len(results)
        print(f"\n📊 Benchmark Results:")
        print(f"   Tests completed: {len(results)}/3")
        print(f"   Average time: {avg_time:.3f}s")
        print(f"   Range: {min(results):.3f}s - {max(results):.3f}s")
        
        # Performance assessment
        if avg_time < 0.5:
            print_status("Excellent performance! Ready for real-time use", "success")
        elif avg_time < 1.0:
            print_status("Good performance. Consider chunking for real-time feel", "success")
        else:
            print_status("Slower performance. Pre-generation recommended", "warning")

def check_system_resources():
    """Check system resources"""
    print_header("System Resources Check")
    
    try:
        import psutil
        
        # Memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"Total memory: {memory_gb:.1f} GB")
        print(f"Available memory: {available_gb:.1f} GB")
        
        if memory_gb >= 16:
            print_status("Sufficient memory for voice cloning", "success")
        else:
            print_status("Limited memory. Consider reducing batch sizes", "warning")
        
        # CPU
        cpu_count = psutil.cpu_count()
        print(f"CPU cores: {cpu_count}")
        
        # Disk space
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        print(f"Free disk space: {free_gb:.1f} GB")
        
        if free_gb < 5:
            print_status("Low disk space. May affect model downloads", "warning")
        else:
            print_status("Sufficient disk space", "success")
            
    except ImportError:
        print_status("psutil not available for system check", "warning")

def provide_recommendations():
    """Provide optimization recommendations"""
    print_header("M1 Max Optimization Recommendations")
    
    recommendations = [
        "🔧 For art installations: Use pre-generation strategy",
        "⚡ For real-time feel: Use sentence chunking (5-8 words)",
        "🚀 For seamless flow: Use parallel generation + playback",
        "💾 Memory management: Clear MPS cache between generations",
        "🎯 Optimal settings: temperature=0.6, exaggeration=0.0",
        "📊 Monitor performance: Track generation times and memory usage"
    ]
    
    for rec in recommendations:
        print(f"  {rec}")

def main():
    """Main verification routine"""
    print("🔍 M1 Max Chatterbox TTS Setup Verification")
    print("This script will verify your installation and benchmark performance")
    
    # Run all checks
    checks = [
        check_python_version(),
        check_conda_environment(),
        check_pytorch_installation(),
        check_audio_dependencies()
    ]
    
    # Check Chatterbox installation and get model
    chatterbox_ok, model = check_chatterbox_installation()
    checks.append(chatterbox_ok)
    
    # System resources
    check_system_resources()
    
    # If all basic checks pass, run benchmark
    if all(checks):
        print_status("All basic checks passed!", "success")
        benchmark_simple_generation(model)
    else:
        print_status("Some checks failed. Fix issues above before benchmarking", "warning")
    
    provide_recommendations()
    
    print_header("Next Steps")
    
    if all(checks):
        print("✅ Setup verified! You can now:")
        print("   1. Run: python m1_optimized_voice.py")
        print("   2. Create your art installation workflow")
        print("   3. Test with your own voice samples")
    else:
        print("❌ Setup incomplete. Please:")
        print("   1. Fix the issues listed above")
        print("   2. Re-run this verification script")
        print("   3. Contact support if problems persist")
    
    print("\n🎉 Verification complete!")

if __name__ == "__main__":
    # Ensure we can import torch for checks
    try:
        import torch
    except ImportError:
        print("❌ PyTorch not available. Please run the setup script first:")
        print("   ./setup_m1_chatterbox.sh")
        sys.exit(1)
        
    main()