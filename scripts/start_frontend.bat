@echo off
title NOVARYX - Frontend Service
cd /d "%~dp0\..\novaryx-web"
echo Starting Next.js Frontend...
if not exist "node_modules" (
    npm install
)
npm run dev
