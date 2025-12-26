# Hospital Appointment System - Start Frontend (Streamlit)
# Run this in PowerShell from project root AFTER starting backend

Write-Host "Starting Hospital Appointment Frontend..." -ForegroundColor Green

# Set execution policy for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set API base URL (adjust if backend is on different port)
$env:API_BASE_URL="http://localhost:8002"

Write-Host "Frontend will open in browser (usually http://localhost:8501)" -ForegroundColor Cyan
Write-Host "API base: $env:API_BASE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Start Streamlit
streamlit run frontend/app.py

