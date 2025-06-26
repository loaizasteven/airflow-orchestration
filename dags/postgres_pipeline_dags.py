from datetime import datetime, timedelta

import csv
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0
}

def saving_to_csv(ti):
    filtered_data = ti.xcom_pull(task_ids='filtering_customers')

    with open('./output/filtered_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Product', 'Price'])
        for row in filtered_data:
            writer.writerow(row)

with DAG(
    dag_id='postgres_pipeline_dags',
    description='Running a pipeline using the Postgres Operator',
    default_args=default_args,
    tags=['postgres', 'pipeline'],
    template_searchpath='/Users/SLoaiza/Documents/GitHub/airflow/sql_statements'
) as dag:

    create_table_customers = SQLExecuteQueryOperator(
        task_id='create_table_customers',
        conn_id='postgres_connection',
        sql='create_table_customers.sql'
    )

    create_table_purchases = SQLExecuteQueryOperator(
        task_id='create_table_purchases',
        conn_id='postgres_connection',
        sql='create_table_customer_purchases.sql'
    )

    insert_customers = SQLExecuteQueryOperator(
        task_id="insert_customers",
        conn_id='postgres_connection',
        sql='insert_customers.sql'
    )

    insert_purchases = SQLExecuteQueryOperator(
        task_id="insert_purchases",
        conn_id='postgres_connection',
        sql='insert_customer_purchases.sql'
    )

    joining_table = SQLExecuteQueryOperator(
        task_id="joining_table",
        conn_id='postgres_connection',
        sql='joining_table.sql'
    )

    filtering_customers = SQLExecuteQueryOperator(
        task_id="filtering_customers",
        conn_id='postgres_connection',
        sql="""
            SELECT name, product, price
            FROM complete_customer_details
            WHERE price BETWEEN %(lower_bound)s AND %(upper_bound)s
        """,
        parameters={
            'lower_bound': 5,
            'upper_bound': 10
        }
    )

    saving_to_csv = PythonOperator(
        task_id='saving_to_csv',
        python_callable=saving_to_csv
    )

    create_table_customers >> create_table_purchases >> \
    [insert_customers, insert_purchases] >> \
    joining_table >> filtering_customers >> saving_to_csv