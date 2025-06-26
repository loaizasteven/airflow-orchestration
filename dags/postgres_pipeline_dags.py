from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0
}

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

    create_table_customers >> create_table_purchases >> insert_customers >> insert_purchases