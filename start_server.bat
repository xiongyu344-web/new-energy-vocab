@echo off
chcp 65001 >nul
title New Energy Vocab Server
echo =======================================
echo   New Energy Vocab - Backend Server
echo =======================================
echo.
cd /d "%~dp0server"

echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt -q

echo.
echo [3/3] Starting server on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server.
echo =======================================
echo.
python app.py
pause
