@echo off
REM Quick Start Script - Laptop Control System (Windows)
REM This script starts all components (Backend, Agent, Mobile App)

echo.
echo ===============================================
echo Laptop Control System - Quick Start (Windows)
echo ===============================================
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found in PATH
    echo Please ensure Python 3.8+ is installed and added to PATH
    pause
    exit /b 1
)

echo [SUCCESS] Python found
echo.

REM ===== Backend Setup =====
echo [INFO] Setting up Backend...

if not exist "backend\venv" (
    echo [INFO] Creating virtual environment for backend...
    cd backend
    python -m venv venv
    cd ..
) else (
    echo [SUCCESS] Backend virtual environment already exists
)

REM Install dependencies
echo [INFO] Installing backend dependencies...
call backend\venv\Scripts\activate
pip install -q -r backend\requirements.txt
call backend\venv\Scripts\deactivate
echo [SUCCESS] Backend dependencies installed
echo.

REM ===== Agent Setup =====
echo [INFO] Setting up Laptop Agent...

if not exist "agent\venv" (
    echo [INFO] Creating virtual environment for agent...
    cd agent
    python -m venv venv
    cd ..
) else (
    echo [SUCCESS] Agent virtual environment already exists
)

REM Install dependencies
echo [INFO] Installing agent dependencies...
call agent\venv\Scripts\activate
pip install -q -r agent\requirements.txt
call agent\venv\Scripts\deactivate
echo [SUCCESS] Agent dependencies installed
echo.

REM ===== Flutter Setup =====
echo [INFO] Setting up Flutter Mobile App...

if not exist "mobile_app\build" (
    echo [INFO] Getting Flutter dependencies...
    cd mobile_app
    flutter pub get >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Flutter pub get might have issues
    )
    cd ..
) else (
    echo [SUCCESS] Flutter app already built
)

echo [SUCCESS] Flutter app setup complete
echo.

REM ===== Environment Setup =====
echo [INFO] Setting up environment files...

if not exist "backend\.env" (
    echo [INFO] Creating backend .env from example...
    copy backend\.env.example backend\.env
    echo [WARNING] Please edit backend\.env with your configuration
) else (
    echo [SUCCESS] Backend .env already exists
)

if not exist "agent\.env" (
    echo [INFO] Creating agent .env from example...
    copy agent\.env.example agent\.env
    echo [WARNING] Please edit agent\.env with your device ID and backend URL
) else (
    echo [SUCCESS] Agent .env already exists
)

echo.
echo ===============================================
echo Setup Complete!
echo ===============================================
echo.

echo Next steps:
echo.
echo 1. BACKEND - In Command Prompt 1:
echo    cd backend
echo    venv\Scripts\activate
echo    python run.py
echo.
echo 2. LAPTOP AGENT - In Command Prompt 2 (after backend starts):
echo    cd agent
echo    venv\Scripts\activate
echo    python agent.py
echo.
echo 3. MOBILE APP - In Command Prompt 3:
echo    cd mobile_app
echo    flutter run
echo.
echo API Documentation:
echo    Swagger: http://localhost:8000/docs
echo    ReDoc:   http://localhost:8000/redoc
echo.

echo [SUCCESS] Ready to start the system!
pause
