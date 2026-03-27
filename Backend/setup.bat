@echo off
title David AI - Setup
echo ==================================================
echo   David AI Assistant - One-Time Setup
echo ==================================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo         Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "..\david_env" (
    echo [*] Creating virtual environment...
    python -m venv "..\david_env"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

REM Upgrade pip
echo [*] Upgrading pip...
"..\david_env\Scripts\python.exe" -m pip install --upgrade pip --quiet

REM Install all requirements
echo [*] Installing dependencies from requirements.txt...
"..\david_env\Scripts\pip.exe" install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some packages failed to install.
    echo          Retrying with verbose output...
    "..\david_env\Scripts\pip.exe" install -r requirements.txt
) else (
    echo [OK] All dependencies installed successfully.
)

REM Check Ollama
echo.
echo [*] Checking Ollama...
ollama --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama is not installed or not in PATH!
    echo          Download from: https://ollama.com/download
) else (
    echo [OK] Ollama found.
    echo [*] Checking for llama3.2 model...
    ollama list | findstr "llama3.2" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [*] Pulling llama3.2 model (this may take a few minutes)...
        ollama pull llama3.2
    ) else (
        echo [OK] llama3.2 model is available.
    )
)

REM Check Frontend
echo.
if exist "..\Frontend\package.json" (
    echo [*] Checking Frontend dependencies...
    cd /d "%~dp0..\Frontend"
    if not exist "node_modules" (
        echo [*] Installing Frontend npm packages...
        npm install
    ) else (
        echo [OK] Frontend node_modules already exist.
    )
    cd /d "%~dp0"
) else (
    echo [INFO] Frontend not found at ..\Frontend - skipping.
)

echo.
echo ==================================================
echo   Setup Complete! Run start.bat to launch David.
echo ==================================================
pause
