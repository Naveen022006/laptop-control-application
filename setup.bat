@echo off
REM Laptop Control Application - Setup Script for Windows
REM This script automates the initial setup of all components

echo.
echo ================================
echo Laptop Control - Setup Script
echo ================================
echo.

REM Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [x] Python is not installed
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i

REM Setup Backend
echo [*] Setting up Backend...
cd backend

if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [*] Installing dependencies...
pip install -r requirements.txt -q

if not exist ".env" (
    echo [*] Creating .env file...
    copy .env.example .env
    echo [OK] Created .env - Please edit with your settings
)

echo [*] Initializing database...
python -c "from app.models.database import create_tables; create_tables()"
echo [OK] Database initialized

cd ..

REM Setup Laptop Agent
echo [*] Setting up Laptop Agent...
cd laptop_agent

if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [*] Installing dependencies...
pip install -r requirements.txt -q

if not exist ".env" (
    echo [*] Creating .env file...
    copy .env.example .env
    echo [OK] Created .env - Please edit with your API token
)

if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots

cd ..

REM Summary
echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo [i] Next steps:
echo 1. Edit backend\.env with your settings
echo 2. Edit laptop_agent\.env with backend URL and API token
echo 3. Register your laptop: curl -X POST http://localhost:8000/devices/register
echo 4. Start backend: cd backend ^&^& uvicorn app.main:app --reload
echo 5. Start agent: cd laptop_agent ^&^& python agent.py
echo 6. Start mobile app: cd mobile_app ^&^& flutter run
echo.
echo [i] Documentation:
echo - Quick Start: See QUICKSTART.md
echo - Full Setup: See SETUP_GUIDE.md
echo - API Docs: See API_DOCUMENTATION.md
echo.
pause
