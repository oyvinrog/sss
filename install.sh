#!/bin/bash
set -e

echo "🔐 Installing SSS (Shamir Secret Sharing) for Bitcoin..."
echo ""

# Check if we're already in the sss directory
if [ -d ".git" ] && [ -f "sss_gui.py" ]; then
    echo "Already in sss directory, skipping clone..."
    SSS_DIR="."
else
    # Clone the repository
    echo "📦 Cloning repository..."
    git clone https://github.com/oyvinrog/sss
    SSS_DIR="sss"
    cd "$SSS_DIR"
fi

# Install system dependencies
echo "📚 Installing system dependencies..."
sudo apt install -y python3-venv proxychains

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment and install Python packages
echo "📥 Installing Python packages..."
source .venv/bin/activate
proxychains pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use SSS:"
echo "  1. Disconnect from internet"
if [ "$SSS_DIR" != "." ]; then
    echo "  2. cd sss"
    echo "  3. source .venv/bin/activate"
    echo "  4. ./run_gui"
else
    echo "  2. source .venv/bin/activate"
    echo "  3. ./run_gui"
fi
echo ""
echo "Or use the command line tools:"
echo "  python3 split.py \"your seed phrase\" shares.txt"
echo "  python3 combine.py shares.txt"