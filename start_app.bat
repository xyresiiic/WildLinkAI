@echo off
title WildLink AI - Startup Launcher
echo ================================================================
echo   🌿 WildLink AI — Multi-Species Wildlife Connectivity Platform
echo ================================================================
echo.

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "WildLink AI - Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo [2/2] Starting Vite React Frontend on http://localhost:5173 ...
start "WildLink AI - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================================================
echo   🚀 Services Launched Successfully!
echo   - Backend API:    http://127.0.0.1:8000/docs
echo   - Frontend App:   http://localhost:5173
echo ================================================================
pause
