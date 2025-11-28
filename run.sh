#!/usr/bin/with-contenv bashio

echo "Starting Migraine Tracker add-on"

# Start the backend server
bashio::log.info "Starting the backend server..."
python3 -m uvicorn migraine_tracker.main:app --host 0.0.0.0 --port 8000
