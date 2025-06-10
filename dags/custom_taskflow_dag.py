import time
import logging
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator


# Set default arguments
default_args = {
    'owner': 'sloaiza'
}

@dag(
    dag_id='custom_taskflow_dag',
    description='A custom taskflow DAG with pythonic syntax',
    start_date=datetime.now(),
    schedule='@once',
    tags=['python', 'airflow', 'taskflow'],
    )
def custom_taskflow_dag():
    
    @task
    def extract_data():
        """Extract data task"""
        logging.info("Extracting data...")
        return {"data": [1, 2, 3, 4, 5]}
    
    @task
    def transform_data(data):
        """Transform data task"""
        logging.info(f"Transforming data: {data}")
        transformed = [x * 2 for x in data["data"]]
        return {"transformed_data": transformed}
    
    @task
    def load_data(data):
        """Load data task"""
        logging.info(f"Loading data: {data}")
        time.sleep(2)  # Simulate loading time
        return "Data loaded successfully"
    
    # Define task dependencies using taskflow syntax
    raw_data = extract_data()
    processed_data = transform_data(raw_data)
    result = load_data(processed_data)
    
    return result

# Instantiate the DAG
dag_instance = custom_taskflow_dag()
