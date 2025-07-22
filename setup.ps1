#!/usr/bin/env pwsh
# Setup script for NYC Taxi Fare Predictor (Windows PowerShell)

Write-Host "🚖 NYC Taxi Fare Predictor - Setup Script" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Installing Backend Dependencies..." -ForegroundColor Cyan

# Install backend dependencies
Set-Location "backend"
try {
    pip install -r requirements.txt
    Write-Host "✅ Backend dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ".."

Write-Host ""
Write-Host "📦 Installing Frontend Dependencies..." -ForegroundColor Cyan

# Install frontend dependencies
Set-Location "frontend"
try {
    npm install
    Write-Host "✅ Frontend dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ".."

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "1. Backend: python run.py" -ForegroundColor White
Write-Host "2. Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Or use the start-app.ps1 script to start both automatically." -ForegroundColor Yellow
