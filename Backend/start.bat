@echo off
title David AI Backend
echo ==================================================
echo   David AI Assistant - Startup Script
echo ==================================================
echo.

cd /d "%~dp0"

REM ── Auto-check: Virtual environment ──
if not exist "..\david_env\Scripts\python.exe" (
    echo [!] Virtual environment not found. Running setup first...
    call setup.bat
    if %ERRORLEVEL% NEQ 0 exit /b 1
)

REM ── Auto-check: Dependencies ──
echo [*] Verifying dependencies...
"..\david_env\Scripts\pip.exe" install -r requirements.txt --quiet >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Some dependencies missing. Installing...
    "..\david_env\Scripts\pip.exe" install -r requirements.txt
)
echo [OK] Dependencies verified.

REM ── Kill anything on port 8001 ──
echo [*] Clearing port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM ── Check Ollama is running ──
echo [*] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Ollama server not detected. Starting Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

REM ── Start the backend ──
echo [*] Starting David AI...
echo.
"..\david_env\Scripts\python.exe" main.py

pause
