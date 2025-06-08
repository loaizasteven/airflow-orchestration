#!/bin/bash

echo "Stopping Airflow processes..."

# Kill all airflow processes
pkill -f "airflow api-server"
pkill -f "airflow scheduler"

echo "Airflow processes stopped."

# Optional: Check if any airflow processes are still running
sleep 2
if pgrep -f airflow > /dev/null; then
    echo "Warning: Some Airflow processes may still be running:"
    pgrep -f airflow
else
    echo "All Airflow processes have been stopped successfully."
fi 