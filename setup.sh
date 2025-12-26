#!/bin/bash
# Quick start script for development

echo "==================================="
echo "Web Crawler - Development Setup"
echo "==================================="

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "Installing backend dependencies..."
cd backend

# Activate based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install -r requirements.txt

echo ""
echo "Running setup tests..."
python test_setup.py

echo ""
echo "==================================="
echo "Setup complete!"
echo "==================================="
echo ""
echo "Available commands:"
echo "  CLI:   python main.py --help"
echo "  API:   python -m flask --app api.app run"
echo "  Tests: pytest"
echo "  Docker: cd .. && docker-compose up"
echo ""
