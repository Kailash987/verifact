#!/bin/bash

# Setup script for Fake News Detection Application

echo "🚀 Setting up Fake News Detection Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL for full functionality."
    echo "   You can run the application with mock data without PostgreSQL."
fi

echo "✅ Prerequisites check passed"

# Setup ML environment
echo "📦 Setting up ML environment..."
cd ml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ ML environment setup complete"

# Setup backend environment
echo "📦 Setting up backend environment..."
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please update with your database configuration."
fi

echo "✅ Backend environment setup complete"

# Setup frontend environment
echo "📦 Setting up frontend environment..."
cd ../frontend
npm install
echo "✅ Frontend environment setup complete"

# Go back to root
cd ..

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start PostgreSQL service (if installed)"
echo "2. Update backend/.env with your database configuration"
echo "3. Train the ML model: cd ml && source venv/bin/activate && python train.py"
echo "4. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Start the frontend: cd frontend && npm start"
echo ""
echo "🌐 Application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
