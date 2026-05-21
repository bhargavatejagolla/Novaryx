@echo off
title NOVARYX - Backend Service
cd /d "%~dp0\.."
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
echo Verifying system health...
python system\health.py
echo.
echo Backend is ready to accept orchestration requests via the Frontend bridge.
pause
