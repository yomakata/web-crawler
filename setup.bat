@echo off
REM Quick start script for Windows

echo ===================================
echo Web Crawler - Development Setup
echo ===================================

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment and install dependencies
echo Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Running setup tests...
python test_setup.py

echo.
echo ===================================
echo Setup complete!
echo ===================================
echo.
echo Available commands:
echo   CLI:   python main.py --help
echo   API:   python -m flask --app api.app run
echo   Tests: pytest
echo   Docker: cd .. ^&^& docker-compose up
echo.

pause
