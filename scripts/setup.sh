#!/bin/bash

# Smarter Case Setup Script
# This script sets up the development environment for the Smarter Case project

set -e

echo "🚀 Setting up Smarter Case development environment..."

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv is not installed. Please install pyenv first."
    echo "   Visit: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# Check if Python 3.11.3 is installed
if ! pyenv versions | grep -q "3.11.3"; then
    echo "📦 Installing Python 3.11.3..."
    pyenv install 3.11.3
fi

# Create virtual environment if it doesn't exist
if ! pyenv versions | grep -q "smarter_case"; then
    echo "🔧 Creating virtual environment 'smarter_case'..."
    pyenv virtualenv 3.11.3 smarter_case
fi

# Set local Python version
echo "🎯 Setting local Python version..."
pyenv local smarter_case

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies if specified
if [ "$1" = "--dev" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data/test_cases data/historical data/models data/cache

# Copy environment template if .env doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Set up pre-commit hooks if dev dependencies are installed
if [ "$1" = "--dev" ] && command -v pre-commit &> /dev/null; then
    echo "🔒 Setting up pre-commit hooks..."
    pre-commit install
fi

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
python -m pytest tests/unit/ -v --tb=short

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Run 'python -m src.main --help' to see available commands"
echo "3. Run 'python -m pytest' to run all tests"
echo ""
echo "🎉 Happy coding!"
