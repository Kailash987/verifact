# Development script for Fake News Detection Application (PowerShell)

Write-Host "🚀 Starting Fake News Detection Application in Development Mode..." -ForegroundColor Green

# Function to cleanup background processes
function Cleanup {
    Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Remove-Job -Force
    exit 0
}

# Set up trap to cleanup on exit
trap Cleanup SIGINT SIGTERM

# Start backend in background
Write-Host "🔧 Starting backend..." -ForegroundColor Blue
Set-Location backend
& .\venv\Scripts\Activate.ps1
Start-Job -ScriptBlock {
    Set-Location backend
    & .\venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} | Out-Null
Set-Location ..

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in background
Write-Host "🎨 Starting frontend..." -ForegroundColor Blue
Set-Location frontend
Start-Job -ScriptBlock {
    Set-Location frontend
    npm start
} | Out-Null
Set-Location ..

Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Application is available at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Wait for all background jobs
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Cleanup
}
