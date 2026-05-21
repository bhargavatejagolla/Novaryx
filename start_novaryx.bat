@echo off
chcp 65001 >nul
title NOVARYX — AI Generation Engine

echo.
echo ================================================
echo   NOVARYX - AI Generation Engine
echo ================================================
echo.

REM ── Load environment ──────────────────────────────
cd /d "%~dp0"

REM ── Check Python ──────────────────────────────────
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ and retry.
    pause
    exit /b 1
)

REM ── Activate venv if available ────────────────────
if exist "venv\Scripts\activate.bat" (
    echo [1/5] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [1/5] No venv found - using system Python
)

REM ── Start Ollama if not running ───────────────────
echo [2/5] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo   Starting Ollama server...
    start /min cmd /c "ollama serve"
    timeout /t 4 /nobreak >nul
    echo   Ollama started.
) else (
    echo   Ollama already running.
)

REM ── Setup tuned models (idempotent) ──────────────
echo [3/5] Setting up tuned models...
python -m system.inference.ollama_setup --pull-only 2>nul
if %errorlevel% neq 0 (
    echo   Model setup skipped (Ollama may still be starting)
)

REM ── Seed RAG knowledge base ───────────────────────
echo [4/5] Seeding RAG knowledge base...
python -m system.rag_engine.seed_knowledge 2>nul
if %errorlevel% neq 0 (
    echo   RAG seeding skipped (chromadb may not be installed)
)

REM ── Health check ──────────────────────────────────
echo [5/5] Running health check...
python system\health.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some health checks failed. Check the output above.
    echo   Generation may still work - continuing...
    echo.
)

echo.
echo ================================================
echo   Starting NOVARYX Web Interface...
echo ================================================
echo.
echo   Backend:  Python ^(novaryx_e2e.py^)
echo   Frontend: http://localhost:3000
echo.
echo   Stop with: Ctrl+C
echo.

REM ── Start Next.js frontend ────────────────────────
cd novaryx-web
if exist "node_modules" (
    npm run dev
) else (
    echo Installing frontend dependencies...
    npm install
    npm run dev
)

pause
