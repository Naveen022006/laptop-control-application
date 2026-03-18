@echo off
echo.
echo ===============================================
echo Laptop Control System - START ALL
echo ===============================================
echo.
echo Starting in 3 terminals...
echo.

REM Start Backend
start "Backend - Laptop Control" cmd /k "cd backend && venv\Scripts\activate && python run.py"

timeout /t 3

REM Start Agent
start "Agent - Laptop Control" cmd /k "cd agent && venv\Scripts\activate && python agent.py"

timeout /t 2

echo.
echo ===============================================
echo Components Starting:
echo 1. Backend: http://localhost:8000
echo 2. Agent: Connecting to backend...
echo 3. Mobile: Already running on your phone!
echo ===============================================
echo.
pause
