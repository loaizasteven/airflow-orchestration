from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=2),  # Max time for task execution
}

# Define the DAG
dag = DAG(
    'hello_world_dag',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule=timedelta(minutes=5),  # Modern Airflow syntax - every 5 minutes for testing
    catchup=False,
    tags=['example'],
)

def print_hello():
    """Simple function to be called by PythonOperator"""
    import logging
    import time
    
    logging.info("Starting hello_python_task")
    print("Hello from Airflow!")
    
    # Add a small delay to ensure task completes properly
    time.sleep(1)
    
    logging.info("Completed hello_python_task successfully")
    return "Hello from Airflow!"

# Define tasks
hello_task = PythonOperator(
    task_id='hello_python_task',
    python_callable=print_hello,
    dag=dag,
)

bash_task = BashOperator(
    task_id='hello_bash_task',
    bash_command='echo "Hello from Bash!"',
    dag=dag,
)

# Set task dependencies
hello_task >> bash_task 