# Hospital Appointment System - Initial Setup
# Run this ONCE before first use

Write-Host "=== Hospital Appointment System - Setup ===" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env from env.example and configure your database/API keys" -ForegroundColor Yellow
    Write-Host "Example: Copy env.example to .env and edit with your settings" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Checking Python version..." -ForegroundColor Cyan
$pythonVersion = python --version
Write-Host "Found: $pythonVersion" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Creating virtual environment..." -ForegroundColor Cyan
py -3.12 -m venv .venv
if (-not $?) {
    Write-Host "Python 3.12 not found. Trying default Python..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host ""
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Cyan
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "Step 4: Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

Write-Host ""
Write-Host "Step 5: Installing dependencies..." -ForegroundColor Cyan
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Step 6: Seeding database..." -ForegroundColor Cyan
python -m backend.app.seed_data

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  1. Open Terminal 1: .\start_backend.ps1" -ForegroundColor White
Write-Host "  2. Open Terminal 2: .\start_frontend.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Then open http://localhost:8501 in your browser" -ForegroundColor Yellow

