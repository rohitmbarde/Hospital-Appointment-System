# Hospital Appointment System - Start Backend API
# Run this in PowerShell from project root

Write-Host "Starting Hospital Appointment Backend API..." -ForegroundColor Green

# Set execution policy for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start uvicorn on port 8002
Write-Host "API will be available at http://127.0.0.1:8002" -ForegroundColor Cyan
Write-Host "API Docs at http://127.0.0.1:8002/docs" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

.\.venv\Scripts\uvicorn.exe backend.app.main:app --reload --port 8002

