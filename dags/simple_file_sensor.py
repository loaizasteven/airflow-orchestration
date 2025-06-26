from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.sensors.filesystem import FileSensor

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0
}

with DAG(
    dag_id='simple_file_sensor',
    description='A simple file sensor DAG',
    default_args=default_args,
    tags=['python', 'sensor'],
) as dag:

    checking_for_file = FileSensor(
        task_id='checking_for_file',
        filepath="/Users/SLoaiza/Documents/GitHub/airflow/tmp/laptops.csv", # ✅ Absolute path,
        poke_interval=10,
        timeout=60 * 10,
    )

    checking_for_file