""" 
Example of a custom XCom DAG (Cross-Communication) using airflow operators. The DAG example
will use the task instance form to pass data between tasks.
"""

import json
import logging
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime


def get_order_price(**kwargs):
    """
    A custom XCom DAG that demonstrates how to pass data between tasks using XComs.
    """
    # task instance
    ti = kwargs['ti']
    
    order_price = {
        'apple': 100,
        'banana': 200,
        'cherry': 300,
    }

    # push the order price to the XComs
    order_price_string = json.dumps(order_price)
    ti.xcom_push(key='order_price', value=order_price_string)
    
def compute_total_price(**kwargs):
    """Compute total price from order data"""
    logging.info("Computing total price...")
    ti = kwargs['ti']

    order_price = json.loads(
        ti.xcom_pull(task_ids='get_order_price', key='order_price'))

    order_price_data = json.loads(order_price)
    total_price = sum(order_price_data.values())

    ti.xcom_push(key='total_price', value=total_price)

def compute_average_price(**kwargs):
    """Compute average price from order data"""
    logging.info("Computing average price...")
    ti = kwargs['ti']

    total_price = ti.xcom_pull(task_ids='compute_total_price', key='total_price')
    order_price = ti.xcom_pull(task_ids='get_order_price', key='order_price')

    order_price_data = json.loads(order_price)

    average_price = total_price / len(order_price_data)

    ti.xcom_push(key='average_price', value=average_price)

def display_results(**kwargs):
    """Display final results"""
    logging.info("Displaying results...")
    ti = kwargs['ti']

    total_price = ti.xcom_pull(task_ids='compute_total_price', key='total_price')
    average_price = ti.xcom_pull(task_ids='compute_average_price', key='average_price')

    logging.info(f"Total price: {total_price}")
    logging.info(f"Average price: {average_price}")

@dag(
    dag_id='custom_xcom_dag',
    start_date=datetime.now(),
)
def custom_xcom_dag():
    """
    Custom XCom DAG that demonstrates data passing between tasks
    """
    
    # Create tasks using PythonOperator
    get_price_task = PythonOperator(
        task_id='get_order_price',
        python_callable=get_order_price
    )
    
    compute_total_task = PythonOperator(
        task_id='compute_total_price',
        python_callable=compute_total_price
    )
    
    compute_avg_task = PythonOperator(
        task_id='compute_average_price',
        python_callable=compute_average_price
    )
    
    display_task = PythonOperator(
        task_id='display_results',
        python_callable=display_results
    )
    
    # Define task dependencies
    get_price_task >> [compute_total_task, compute_avg_task] >> display_task

# Instantiate the DAG
dag_instance = custom_xcom_dag()