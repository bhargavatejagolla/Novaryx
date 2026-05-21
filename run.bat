@echo off
title NOVARYX - Unified Workspace Manager
cls
echo ============================================================
echo   NOVARYX - Autonomous Application Generator
echo ============================================================
echo.

:: 1. Verify and boot Ollama silently
echo [1/3] Verifying Ollama Inference Server...
curl -s -I http://localhost:11434/api/tags >nul
if errorlevel 1 (
    echo       Ollama is not running. Starting it in the background...
    start /min "Ollama Server" ollama serve
    timeout /t 5 /nobreak >nul
) else (
    echo       Ollama is online and ready.
)

:: 2. Verify backend health inline
echo.
echo [2/3] Verifying System Health ^& RAG Seed status...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python system\health.py
if errorlevel 1 (
    echo.
    echo ❌ Pre-flight System Health verification failed!
    echo    Please check the errors above before launching the UI.
    pause
    exit /b 1
)

:: 3. Launch Next.js Frontend inline in the same window
echo.
echo [3/3] Launching Frontend Interface (Next.js)...
echo       Open your browser to: http://localhost:3000
echo.
cd novaryx-web
npm run dev
