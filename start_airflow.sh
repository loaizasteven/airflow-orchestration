#!/bin/bash

# Set Airflow Home
export AIRFLOW_HOME=$(pwd)/airflow_home

# Start Airflow API Server and Scheduler
echo "Starting Airflow..."
echo "AIRFLOW_HOME is set to: $AIRFLOW_HOME"

# Stop any existing processes first
echo "Stopping any existing Airflow processes..."
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "airflow api-server" 2>/dev/null || true
sleep 2

# Create an admin user if it doesn't exist
echo "Creating admin user..."
airflow users create-user \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin 2>/dev/null || echo "User may already exist"

# Start API server (web UI) in background
echo "Starting Airflow API server on port 8080..."
airflow api-server --port 8080 --daemon

# Start scheduler in background  
echo "Starting Airflow scheduler..."
airflow scheduler --daemon

echo "Airflow is starting up..."
echo "Web UI will be available at: http://localhost:8080"
echo "Username: admin"
echo "Password: admin"
echo ""
echo "To stop Airflow, run: pkill -f airflow" 