#!/bin/bash

# AdPoster Server Kill Script
# This script stops the running Flask development server

# Find all server processes
SERVER_PIDS=$(ps aux | grep "web_interface.py" | grep -v grep | awk '{print $2}')

if [ -z "$SERVER_PIDS" ]; then
    echo "No AdPoster server process found running."
    exit 0
fi

echo "Found AdPoster server process(es): $SERVER_PIDS"
echo "Stopping server(s)..."

# Kill all processes gracefully first
for PID in $SERVER_PIDS; do
    kill $PID 2>/dev/null
done

# Wait a moment for graceful shutdown
sleep 2

# Check if any are still running and force kill if needed
REMAINING_PIDS=""
for PID in $SERVER_PIDS; do
    if ps -p $PID > /dev/null 2>&1; then
        REMAINING_PIDS="$REMAINING_PIDS $PID"
    fi
done

if [ -n "$REMAINING_PIDS" ]; then
    echo "Server(s) didn't stop gracefully, force killing..."
    for PID in $REMAINING_PIDS; do
        kill -9 $PID 2>/dev/null
    done
    sleep 1
fi

# Final check
ALL_KILLED=true
for PID in $SERVER_PIDS; do
    if ps -p $PID > /dev/null 2>&1; then
        ALL_KILLED=false
        break
    fi
done

if [ "$ALL_KILLED" = true ]; then
    echo "AdPoster server stopped successfully."
else
    echo "Failed to stop some server processes: $REMAINING_PIDS"
    exit 1
fi