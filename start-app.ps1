#!/usr/bin/env pwsh
# Start script for NYC Taxi Fare Predictor (Windows PowerShell)

Write-Host "🚖 Starting NYC Taxi Fare Predictor..." -ForegroundColor Yellow

# Function to start backend
function Start-Backend {
    Write-Host "🔧 Starting Backend API..." -ForegroundColor Cyan
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python run.py"
}

# Function to start frontend
function Start-Frontend {
    Write-Host "🌐 Starting Frontend..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3  # Give backend time to start
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
}

# Start both services
Start-Backend
Start-Frontend

Write-Host ""
Write-Host "✅ Both services are starting..." -ForegroundColor Green
Write-Host "📍 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "🌐 Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "⏹️ Close the terminal windows to stop the services" -ForegroundColor Yellow
