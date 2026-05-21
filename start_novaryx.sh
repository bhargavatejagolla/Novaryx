#!/bin/bash
echo "========================================"
echo "  NOVARYX - Starting All Services"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/3] Starting Python Backend..."
cd novaryx-web && npm run backend:start &
BACKEND_PID=$!

echo "[2/3] Starting Next.js Frontend..."
npm run dev &
FRONTEND_PID=$!

sleep 5

echo ""
echo "========================================"
echo "  NOVARYX is running!"
echo "  Frontend: http://localhost:3000"
echo "  WebSocket: ws://localhost:9001"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
