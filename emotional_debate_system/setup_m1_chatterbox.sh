#!/bin/bash

# M1 Max Optimized Chatterbox TTS Setup Script
# For emotional_debate_system with Claude redesign

set -e

echo "🚀 Setting up M1 Max optimized environment with Chatterbox TTS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if conda is available
if ! command -v conda &> /dev/null; then
    print_error "Conda not found. Please install Anaconda or Miniconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    print_warning "This script is optimized for Apple Silicon (M1/M2). You may experience different performance."
fi

# Remove existing environment if it exists
ENV_NAME="voice_m1_chatterbox"
if conda env list | grep -q "$ENV_NAME"; then
    print_warning "Removing existing $ENV_NAME environment..."
    conda env remove -n "$ENV_NAME" -y
fi

print_status "Creating clean conda environment: $ENV_NAME"
conda create -n "$ENV_NAME" python=3.11 -y

print_status "Activating environment..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# Verify we're in the right environment
if [[ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]]; then
    print_error "Failed to activate environment. Please run: conda activate $ENV_NAME"
    exit 1
fi

print_status "Installing PyTorch with MPS support (critical for M1)..."
pip install torch torchvision torchaudio

print_status "Installing Chatterbox TTS..."
pip install chatterbox-tts

print_status "Installing audio libraries..."
pip install sounddevice soundfile numpy

print_status "Installing additional dependencies for optimization..."
pip install psutil  # For memory monitoring
pip install threading-utils  # For parallel processing
pip install queue-utils  # For audio queuing

print_status "Installing development dependencies..."
pip install jupyter  # For testing and development
pip install matplotlib  # For performance visualization

# Create requirements file for this specific setup
print_status "Creating requirements file..."
cat > requirements_m1_chatterbox.txt << EOF
# M1 Max Optimized Chatterbox TTS Requirements
# Generated: $(date)

# Core ML/Audio
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
chatterbox-tts>=1.0.0

# Audio processing
sounddevice>=0.4.6
soundfile>=0.12.1
numpy>=1.24.0

# Performance and utilities
psutil>=5.9.0
threading-utils
queue-utils

# Development
jupyter>=1.0.0
matplotlib>=3.7.0

# Environment management
python-dotenv>=1.0.0
pydantic>=2.5.0
EOF

print_status "Testing MPS availability..."
python3 << 'EOF'
import torch
import sys

print(f"PyTorch version: {torch.__version__}")
mps_available = torch.backends.mps.is_available()
mps_built = torch.backends.mps.is_built()

print(f"MPS available: {mps_available}")
print(f"MPS built: {mps_built}")

if mps_available and mps_built:
    print("✅ MPS is working correctly!")
    sys.exit(0)
else:
    print("❌ MPS is not available. Will attempt to fix...")
    sys.exit(1)
EOF

MPS_STATUS=$?

if [ $MPS_STATUS -ne 0 ]; then
    print_warning "MPS not working, attempting to reinstall PyTorch..."
    pip uninstall torch torchvision torchaudio -y
    pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
    
    print_status "Re-testing MPS..."
    python3 << 'EOF'
import torch
mps_available = torch.backends.mps.is_available()
mps_built = torch.backends.mps.is_built()

if mps_available and mps_built:
    print("✅ MPS is now working correctly!")
else:
    print("❌ MPS still not available. Check your macOS version (requires 12.3+)")
    exit(1)
EOF
fi

print_status "Creating activation script..."
cat > activate_m1_chatterbox.sh << EOF
#!/bin/bash
# Quick activation script for M1 Chatterbox environment

echo "Activating M1 Chatterbox environment..."
eval "\$(conda shell.bash hook)"
conda activate voice_m1_chatterbox

# Set environment variables for optimal performance
export PYTORCH_ENABLE_MPS_FALLBACK=1
export OMP_NUM_THREADS=8  # M1 Max has 10 cores, leave 2 for system
export MKL_NUM_THREADS=8

echo "Environment activated! MPS support enabled."
echo "Run 'python verify_m1_setup.py' to test performance."
EOF

chmod +x activate_m1_chatterbox.sh

print_status "Environment setup complete!"
echo ""
echo "To activate this environment in the future, run:"
echo "  conda activate voice_m1_chatterbox"
echo "  or"
echo "  ./activate_m1_chatterbox.sh"
echo ""
echo "Next steps:"
echo "1. Run: python verify_m1_setup.py"
echo "2. Test with: python m1_optimized_voice.py"
echo ""
print_status "Setup completed successfully! 🎉"