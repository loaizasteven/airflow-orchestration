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
}

# Define the DAG
dag = DAG(
    'hello_world_dag',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example'],
)

def print_hello():
    """Simple function to be called by PythonOperator"""
    print("Hello from Airflow!")
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