#!/bin/bash
# Setup script for real API testing

echo "🔧 Setting up Real API Test Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Settings
DEMO_MODE=false
HIPAA_MODE=true
enable_rag=true

# Database
DB_URL=sqlite:///data/medigator.db

# CORS
CORS_ORIGINS_CSV=http://localhost:5173,http://localhost:3000,http://localhost:8080
EOF
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and add your OpenAI API key"
else
    echo "✅ .env file already exists"
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set in environment"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo "Or edit the .env file"
else
    echo "✅ OPENAI_API_KEY is set: ${OPENAI_API_KEY:0:8}..."
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found"
    echo "Creating virtual environment with Python 3.12..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."

python -c "import openai" 2>/dev/null && echo "✅ openai installed" || echo "❌ openai not installed - run: pip install openai"
python -c "import fastapi" 2>/dev/null && echo "✅ fastapi installed" || echo "❌ fastapi not installed - run: pip install fastapi uvicorn"
python -c "import pydantic_settings" 2>/dev/null && echo "✅ pydantic-settings installed" || echo "❌ pydantic-settings not installed - run: pip install pydantic-settings"

# Check if RAG index exists
if [ -f "rag_index/index.faiss" ]; then
    echo "✅ RAG index found"
else
    echo "⚠️  RAG index not found - RAG features may not work"
    echo "To build RAG index, run: python -m api.services.rag.index"
fi

echo ""
echo "🚀 Ready for real API testing!"
echo "Run: python test_real_api.py"
