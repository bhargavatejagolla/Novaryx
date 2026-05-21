@echo off
title NOVARYX - Autonomous Orchestration Manager
cd /d "%~dp0"

echo ================================================
echo   NOVARYX - Infrastructure Boot
echo ================================================
echo.

echo [1/3] Starting Inference Service (Ollama)...
start "NOVARYX - Ollama Service" cmd /c "scripts\start_ollama.bat"
timeout /t 3 /nobreak >nul

echo [2/3] Starting Backend Service...
start "NOVARYX - Backend Service" cmd /c "scripts\start_backend.bat"

echo [3/3] Starting Frontend UI...
start "NOVARYX - Frontend Service" cmd /c "scripts\start_frontend.bat"

echo.
echo All services launched in separate windows!
echo Close this window to exit the boot manager.
pause >nul
