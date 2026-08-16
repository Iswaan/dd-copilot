#!/bin/bash
echo "Starting AI Due Diligence Copilot..."

# Start Backend
echo "Starting FastAPI Backend..."
./venv/Scripts/python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Starting React Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Both servers running. Press Ctrl+C to stop."

# Wait for any process to exit
wait -n

# Kill all on exit
kill $BACKEND_PID $FRONTEND_PID
