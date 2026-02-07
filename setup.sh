#!/bin/bash
# Setup script for Multi-Agent Game Testing System

echo "=================================="
echo "Setup: Multi-Agent Game Tester"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.8+
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python version is compatible"
else
    echo "✗ Python 3.8+ is required"
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
echo ""

# Install dependencies
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Dependencies installed successfully"
else
    echo ""
    echo "✗ Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Quick Start:"
echo "  1. Test a game:"
echo "     python main.py --url 'https://example.com/game'"
echo ""
echo "  2. Run demo:"
echo "     python demo.py"
echo ""
echo "  3. Get help:"
echo "     python main.py --help"
echo ""
echo "For more information, see README.md"
echo ""
