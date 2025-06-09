"""
Classification Training Script

This script provides a complete pipeline for training classification models
including data preprocessing, model training, evaluation, and saving.
"""
from datetime import datetime, timedelta
from pathlib import Path
import logging

from airflow import DAG
# Use traditional import paths for better macOS compatibility
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Remove pandas and sklearn imports from module level
# import pandas as pd
# from sklearn.datasets import make_classification, load_iris

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=10),  # Max time for task execution
}

# Define the DAG
dag = DAG(
    'custom_training_dag',
    default_args=default_args,
    description='A simple classification training DAG',
    schedule=timedelta(minutes=5), 
    catchup=False,
    tags=['machine-learning', 'airflow'],
)

# Custom python code
def load_data(data_path: str = None, save_data: bool = False, **context):
    """
    Load data from file or generate sample data for demonstration.
    
    Args:
        data_path: Path to CSV file
        save_data: Whether to save the data to disk
        **context: Airflow context (task_instance, dag_run, etc.)
    """
    # Import pandas and sklearn inside the function to avoid DAG parsing issues on macOS
    import pandas as pd
    from sklearn.datasets import load_iris
    
    # Access Airflow context information
    task_instance = context.get('task_instance')
    dag_run = context.get('dag_run')
    logger.info(f"Running task: {task_instance.task_id}")
    logger.info(f"DAG run ID: {dag_run.run_id}")
    
    if data_path and Path(data_path).exists():
        logger.info(f"Loading data from {data_path}")
        data = pd.read_csv(data_path)
    else:
        logger.info("Generating sample classification data from iris dataset")
        iris = load_iris()
        data = pd.DataFrame(iris.data, columns=iris.feature_names)
        data['target'] = iris.target

        logger.info(f"Save set to {save_data}")
        if save_data:
            # Use run_id in filename to make it unique per run
            filename = f'sample_data_{dag_run.run_id}.csv'
            data.to_csv(filename, index=False)
            logger.info(f"Sample data saved to {filename}")

    return data

# Define the DAG steps
bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello from Airflow bash task!"',
    dag=dag,
)

bash_task3 = BashOperator(
    task_id='bash_task3',
    bash_command='which python',
    dag=dag,
)

bash_task2 = BashOperator(
    task_id='bash_task2',
    bash_command='echo "Second bash task completed successfully!"',
    dag=dag,
)

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    op_kwargs={
        'data_path': None,
        'save_data': True
    },
    dag=dag,
)
load_data_task.doc_md = """
This task loads data from a file or generates sample data from the iris dataset.

## Parameters
- `data_path`: Path to the data file. If not provided, sample data from the iris dataset will be generated.

## Returns
- `data`: A pandas DataFrame containing the loaded data.
"""

# Define the DAG workflow
bash_task >> bash_task3 >> [load_data_task, bash_task2]
