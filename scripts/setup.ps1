# Setup script for Fake News Detection Application (PowerShell)

Write-Host "🚀 Setting up Fake News Detection Application..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 is required but not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is required but not installed. Please install Node.js 16+ first." -ForegroundColor Red
    exit 1
}

# Check if PostgreSQL is installed
try {
    $psqlVersion = psql --version 2>&1
    Write-Host "✅ PostgreSQL found: $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  PostgreSQL is not installed. Please install PostgreSQL for full functionality." -ForegroundColor Yellow
    Write-Host "   You can run the application with mock data without PostgreSQL." -ForegroundColor Yellow
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Setup ML environment
Write-Host "📦 Setting up ML environment..." -ForegroundColor Blue
Set-Location ml
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "✅ ML environment setup complete" -ForegroundColor Green

# Setup backend environment
Write-Host "📦 Setting up backend environment..." -ForegroundColor Blue
Set-Location ..\backend
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Copy environment file
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "📝 Created .env file. Please update with your database configuration." -ForegroundColor Yellow
}

Write-Host "✅ Backend environment setup complete" -ForegroundColor Green

# Setup frontend environment
Write-Host "📦 Setting up frontend environment..." -ForegroundColor Blue
Set-Location ..\frontend
npm install
Write-Host "✅ Frontend environment setup complete" -ForegroundColor Green

# Go back to root
Set-Location ..

Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Start PostgreSQL service (if installed)" -ForegroundColor White
Write-Host "2. Update backend\.env with your database configuration" -ForegroundColor White
Write-Host "3. Train ML model: cd ml && .\venv\Scripts\Activate.ps1 && python train.py" -ForegroundColor White
Write-Host "4. Start backend: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "5. Start frontend: cd frontend && npm start" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Application will be available at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
