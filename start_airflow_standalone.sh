#!/bin/bash

# Set Airflow Home
export AIRFLOW_HOME=$(pwd)/airflow_home

echo "Starting Airflow in standalone mode..."
echo "AIRFLOW_HOME is set to: $AIRFLOW_HOME"
echo ""
echo "This will start both the webserver and scheduler together."
echo "The first run will create an admin user automatically."
echo ""
echo "Starting Airflow standalone..."

# Start Airflow in standalone mode
airflow standalone 