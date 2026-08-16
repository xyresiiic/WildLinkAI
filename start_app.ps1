# WildLink AI — PowerShell Launcher
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  🌿 WildLink AI — Multi-Species Wildlife Connectivity Platform" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

$root = $PSScriptRoot

Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting Vite React Frontend on http://localhost:5173 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm run dev"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  🚀 Services Launched Successfully!" -ForegroundColor Green
Write-Host "  - Backend API:    http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  - Frontend App:   http://localhost:5173" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Green
