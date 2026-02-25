#!/bin/bash
# Rally Timing - Start both backend and frontend servers

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Rally Timing System ==="
echo ""

# Start Flask API
echo "Starting backend API on port 5000..."
cd "$PROJECT_DIR/backend"
python run.py &
BACKEND_PID=$!

# Start frontend static server
echo "Starting frontend on port 8080..."
cd "$PROJECT_DIR/frontend"
python -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "Rally Timing is running!"
echo "  API:      http://localhost:5000/api/health"
echo "  Frontend: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C to kill both processes
trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
