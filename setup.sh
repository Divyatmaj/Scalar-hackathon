#!/bin/bash

# Quick Start Script for AI Interview Prep RL Environment

echo "🚀 AI Interview Preparation RL Environment - Quick Start"
echo "========================================================"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
echo ""

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python 3 found"

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi
echo "✅ Node.js found"

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm"
    exit 1
fi
echo "✅ npm found"

echo ""
echo "========================================================"
echo "📦 Installing Dependencies..."
echo "========================================================"
echo ""

# Backend setup
echo "🐍 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python packages..."
pip install -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""

# Frontend setup
echo "⚛️  Setting up frontend..."
cd ../frontend

echo "Installing Node packages..."
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""

# Back to root
cd ..

echo "========================================================"
echo "✅ Installation Complete!"
echo "========================================================"
echo ""
echo "📝 Optional: Set OpenAI API Key (for real LLM responses)"
echo "   export OPENAI_API_KEY='your-key-here'"
echo ""
echo "   Note: System works with mock answers if no API key set"
echo ""
echo "========================================================"
echo "🎯 To start the application:"
echo "========================================================"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "========================================================"
echo "🧪 To test the backend first:"
echo "========================================================"
echo ""
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python test_env.py"
echo ""
echo "Happy Hacking! 🎉"
