#!/bin/bash
# Fix Python version inconsistencies

echo "🔧 Fixing Python Version Inconsistencies..."

# Check current Python versions
echo "🐍 Current Python versions:"
echo "  python: $(python --version 2>&1)"
echo "  python3: $(python3 --version 2>&1)"

# Check which Python versions are available
echo "📋 Available Python versions:"
ls -la /Library/Frameworks/Python.framework/Versions/ 2>/dev/null || echo "  No system Python frameworks found"

# Remove old virtual environment if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create new virtual environment with Python 3.12
echo "🆕 Creating new virtual environment with Python 3.12..."
if command -v python3.12 &> /dev/null; then
    python3.12 -m venv venv
elif [ -f "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12" ]; then
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 -m venv venv
else
    echo "❌ Python 3.12 not found. Using default python3..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Verify Python version in virtual environment
echo "✅ Virtual environment Python version: $(python --version)"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install basic dependencies
echo "📦 Installing basic dependencies..."
pip install openai pydantic-settings fastapi uvicorn

# Verify installations
echo "🔍 Verifying installations..."
python -c "import openai; print('✅ openai:', openai.__version__)" 2>/dev/null || echo "❌ openai not working"
python -c "import fastapi; print('✅ fastapi:', fastapi.__version__)" 2>/dev/null || echo "❌ fastapi not working"
python -c "import pydantic_settings; print('✅ pydantic-settings installed')" 2>/dev/null || echo "❌ pydantic-settings not working"

echo ""
echo "🎉 Python version cleanup completed!"
echo "✅ All components now use Python 3.12"
echo ""
echo "To use the project:"
echo "  source venv/bin/activate"
echo "  python --version  # Should show Python 3.12.x"
