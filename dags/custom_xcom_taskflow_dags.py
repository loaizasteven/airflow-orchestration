import time

from datetime import datetime, timedelta
from airflow.decorators import dag, task

default_args = {
    'owner': 'sloaiza',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='cross-task-communication-dag',
    default_args=default_args,
    start_date=datetime.now(),
    schedule=None,
    tags=['python', 'airflow', 'taskflow', 'xcom'],
)
def custom_xcom_taskflow_dag():
    @task
    def get_order_price(**kwargs):
        """
        A custom XCom DAG that demonstrates how to pass data between tasks using XComs.
        """
        order_price = {
            'apple': 100,
            'banana': 200,
            'cherry': 300,
        }

        # pushed to XComs automatically
        return order_price

    @task
    def compute_sum(order_price_data: dict):
        total = 0

        for order in order_price_data:
            total += order_price_data[order]

        return total

    @task
    def compute_average(order_price_data:dict):
        total = 0
        count = 0

        for order in order_price_data:
            total += order_price_data[order]
            count += 1

        return total / count

    @task
    def display_results(total: int, average: int):
        print(f"Total price: {total}")
        print(f"Average price: {average}")

    order_price_data = get_order_price()
    total = compute_sum(order_price_data)
    average = compute_average(order_price_data)
    display_results(total, average)

custom_xcom_taskflow_dag()
        