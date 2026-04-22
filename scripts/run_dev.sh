#!/bin/bash

# Development script for Fake News Detection Application

echo "🚀 Starting Fake News Detection Application in Development Mode..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping all services..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Services started!"
echo ""
echo "🌐 Application is available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background jobs
wait
