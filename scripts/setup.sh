#!/bin/bash
# Multi-Agent Framework Setup Script

set -e

echo "Setting up Multi-Agent Framework..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)' || echo "")
required_version="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
    echo "Python version $python_version is compatible"
else
    echo "Python 3.9+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"

# Setup pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cp .env.example .env
    echo "Please edit .env with your API keys"
fi

# Create initial directories
echo "Creating additional directories..."
mkdir -p logs
mkdir -p cache
mkdir -p screenshots

# Run initial tests
echo "Running initial tests..."
pytest tests/unit --verbose || echo "Some tests may fail without API keys - this is normal"

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Test: python -m src.cli list-agents"
echo "4. Start building your agents!"
