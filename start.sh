#!/bin/bash

# RAG AI Assistant Startup Script

echo "🚀 Starting RAG AI Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."

# Configurar carpetas temporales locales para evitar llenar /tmp del sistema
export TMPDIR="$(pwd)/.tmp_build"
export PIP_CACHE_DIR="$(pwd)/.pip_cache"
mkdir -p "$TMPDIR" "$PIP_CACHE_DIR"

pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys!"
    echo "   - OPENAI_API_KEY=your_openai_api_key_here"
    echo ""
    echo "Press Enter to continue after setting up your .env file..."
    read
fi

# Start the application
echo "🎉 Launching RAG AI Assistant..."
python app.py --host 0.0.0.0

echo "👋 RAG AI Assistant stopped."
