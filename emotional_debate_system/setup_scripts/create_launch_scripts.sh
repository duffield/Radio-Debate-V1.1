#!/bin/bash

echo "🚀 Creating launch scripts..."

# Create setup.sh
cat > setup.sh << 'EOF'
#!/bin/bash

echo "🔧 Setting up Emotional AI Debate System"
echo "="*60

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing..."
    brew install ollama
fi

# Check if espeak-ng is installed  
if ! command -v espeak-ng &> /dev/null; then
    echo "❌ espeak-ng not found. Installing..."
    brew install espeak-ng
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies (this may take 5-10 minutes)..."
pip install -r requirements.txt

echo ""
echo "🤖 Checking Ollama models..."
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "📥 Downloading llama3.1:8b model (~5GB, may take 5-10 minutes)..."
    ollama pull llama3.1:8b
else
    echo "✅ llama3.1:8b already installed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. source venv/bin/activate"
echo "2. ollama serve  # In a separate terminal"
echo "3. python src/main.py"
EOF

chmod +x setup.sh

echo "✅ Created setup.sh"

# Create run.sh
cat > run.sh << 'EOF'
#!/bin/bash

echo "🦎 Starting Emotional AI Debate System"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

source venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🔧 Ollama not detected. Starting Ollama service..."
    echo "   (This will run in the background)"
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "✅ Ollama started"
fi

# Run the main script
python src/main.py "$@"

deactivate
EOF

chmod +x run.sh

echo "✅ Created run.sh"
echo ""
echo "🎉 Launch scripts complete!"
echo ""
echo "All setup files created! Ready to install."