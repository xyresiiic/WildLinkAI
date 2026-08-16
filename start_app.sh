#!/usr/bin/env bash
# WildLink AI — Linux/macOS Startup Script

echo "================================================================"
echo "  🌿 WildLink AI — Multi-Species Wildlife Connectivity Platform"
echo "================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..."
(cd "$SCRIPT_DIR/backend" && source venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

sleep 2

echo "[2/2] Starting Vite React Frontend on http://localhost:5173 ..."
(cd "$SCRIPT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "================================================================"
echo "  🚀 Services Running:"
echo "  - Backend API:    http://127.0.0.1:8000/docs (PID $BACKEND_PID)"
echo "  - Frontend App:   http://localhost:5173      (PID $FRONTEND_PID)"
echo "================================================================"
echo "Press Ctrl+C to terminate all services."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
