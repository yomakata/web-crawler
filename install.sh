#!/bin/bash

# Web Crawler - Complete Installation Script
# This script sets up both backend and frontend

set -e

echo "🚀 Web Crawler - Complete Installation"
echo "========================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ npm $NPM_VERSION found"

echo ""
echo "📦 Installing Backend Dependencies..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing Python packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Backend dependencies installed"
cd ..

echo ""
echo "📦 Installing Frontend Dependencies..."
cd frontend

# Install frontend dependencies
echo "Installing npm packages..."
npm install --silent

echo "✅ Frontend dependencies installed"
cd ..

echo ""
echo "⚙️  Setting up environment..."

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

# Copy frontend .env if it doesn't exist
if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend/.env file..."
    cp frontend/.env.example frontend/.env
    echo "✅ frontend/.env file created"
else
    echo "ℹ️  frontend/.env file already exists"
fi

# Create output directory
if [ ! -d "output" ]; then
    echo "Creating output directory..."
    mkdir -p output
    echo "✅ output directory created"
fi

echo ""
echo "✅ Installation Complete!"
echo ""
echo "📚 Next Steps:"
echo ""
echo "Option 1: Start with Docker (Recommended)"
echo "  docker-compose up -d"
echo "  Open http://localhost:3000"
echo ""
echo "Option 2: Start Backend API"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m flask --app api.app run"
echo ""
echo "Option 3: Start Frontend Dev Server"
echo "  cd frontend"
echo "  npm run dev"
echo "  Open http://localhost:3000"
echo ""
echo "Option 4: Use CLI"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py --url https://example.com"
echo ""
echo "📖 For more information, see:"
echo "  - README.md"
echo "  - GETTING_STARTED.md"
echo "  - FRONTEND_QUICKSTART.md"
echo ""
echo "🎉 Happy Crawling!"
