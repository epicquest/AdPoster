#!/bin/bash

# AdPoster Server Kill Script
# This script stops the running Flask development server

# Find all server processes with multiple patterns
SERVER_PIDS=$(ps aux | grep -E "(web_interface|app\.web_interface|python.*web_interface)" | grep -v grep | awk '{print $2}')

# Also check for processes using port 5000
PORT_PIDS=$(lsof -ti :5000 2>/dev/null || true)

# Combine all PIDs
ALL_PIDS="$SERVER_PIDS $PORT_PIDS"
ALL_PIDS=$(echo $ALL_PIDS | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ] || [ "$ALL_PIDS" = " " ]; then
    echo "No AdPoster server process found running."
    echo "Checking for any process on port 5000..."
    lsof -i :5000 2>/dev/null || echo "Port 5000 is free."
    exit 0
fi

echo "Found AdPoster server process(es): $ALL_PIDS"
echo "Stopping server(s)..."

# Kill all processes gracefully first
for PID in $ALL_PIDS; do
    if [ -n "$PID" ] && [ "$PID" != " " ]; then
        echo "Killing PID: $PID"
        kill $PID 2>/dev/null
    fi
done

# Wait a moment for graceful shutdown
sleep 2

# Check if any are still running and force kill if needed
REMAINING_PIDS=""
for PID in $ALL_PIDS; do
    if [ -n "$PID" ] && [ "$PID" != " " ] && ps -p $PID > /dev/null 2>&1; then
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
for PID in $ALL_PIDS; do
    if [ -n "$PID" ] && [ "$PID" != " " ] && ps -p $PID > /dev/null 2>&1; then
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