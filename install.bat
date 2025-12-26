@echo off
REM Web Crawler - Complete Installation Script for Windows
REM This script sets up both backend and frontend

echo ========================================
echo Web Crawler - Complete Installation
echo ========================================
echo.

echo Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)

for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found
echo.

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed.
    exit /b 1
)

for /f %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm %NPM_VERSION% found
echo.

echo Installing Backend Dependencies...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python packages...
call venv\Scripts\activate.bat
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

echo [OK] Backend dependencies installed
cd ..
echo.

echo Installing Frontend Dependencies...
cd frontend

REM Install frontend dependencies
echo Installing npm packages...
call npm install --silent

echo [OK] Frontend dependencies installed
cd ..
echo.

echo Setting up environment...

REM Copy .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul
    echo [OK] .env file created
) else (
    echo [INFO] .env file already exists
)

REM Copy frontend .env if it doesn't exist
if not exist "frontend\.env" (
    echo Creating frontend\.env file...
    copy frontend\.env.example frontend\.env >nul
    echo [OK] frontend\.env file created
) else (
    echo [INFO] frontend\.env file already exists
)

REM Create output directory
if not exist "output" (
    echo Creating output directory...
    mkdir output
    echo [OK] output directory created
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next Steps:
echo.
echo Option 1: Start with Docker (Recommended)
echo   docker-compose up -d
echo   Open http://localhost:3000
echo.
echo Option 2: Start Backend API
echo   cd backend
echo   venv\Scripts\activate
echo   python -m flask --app api.app run
echo.
echo Option 3: Start Frontend Dev Server
echo   cd frontend
echo   npm run dev
echo   Open http://localhost:3000
echo.
echo Option 4: Use CLI
echo   cd backend
echo   venv\Scripts\activate
echo   python main.py --url https://example.com
echo.
echo For more information, see:
echo   - README.md
echo   - GETTING_STARTED.md
echo   - FRONTEND_QUICKSTART.md
echo.
echo Happy Crawling!
echo.
pause
