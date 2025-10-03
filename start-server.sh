#!/bin/bash

# AdPoster Server Startup Script
# This script starts the Flask development server in the background

# Set the project root directory (relative to script location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Set PYTHONPATH and run the server in background
cd "$PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT" "$PROJECT_ROOT/venv/bin/python" -m app.web_interface &

echo "AdPoster server started in background (PID: $!)"
echo "Server running at: http://127.0.0.1:5000"
echo "To stop the server, run: kill $!"