from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0
}

with DAG(
    dag_id='pipeine_with_sql_sensor',
    description='A pipeline with a SQL sensor',
    default_args=default_args,
    tags=['sql', 'sensor', 'postgres'],
) as dag:

    create_laptops_table = SQLExecuteQueryOperator(
        task_id='create_laptops_table',
        conn_id='postgres_connection_laptop_db',
        sql="""
            CREATE TABLE IF NOT EXISTS laptops (
                id SERIAL PRIMARY KEY,
                company VARCHAR(255),
                product VARCHAR(255),
                type_name VARCHAR(255),
                price_euros NUMERIC(10, 2)
            )
        """,
    )

    create_premium_laptops_table = SQLExecuteQueryOperator(
        task_id='create_premium_laptops_table',
        conn_id='postgres_connection_laptop_db',
        sql="""
            CREATE TABLE IF NOT EXISTS premium_laptops (
                id SERIAL PRIMARY KEY,
                company VARCHAR(255),
                product VARCHAR(255),
                type_name VARCHAR(255),
                price_euros NUMERIC(10, 2)
                """
    )

    wait_for_premium_laptops = SqlSensor(
        task_id='wait_for_premium_laptops',
        conn_id='postgres_connection_laptop_db',
        sql='SELECT EXISTS( SELECT 1 FROM premium_laptops where price_euros > 500 )',
        timeout=60 * 10,
        poke_interval=10,
    )

    insert_data_into_premium_laptops_table = SQLExecuteQueryOperator(
        task_id='insert_data_into_premium_laptops_table',
        conn_id='postgres_connection_laptop_db',
        sql="""
            INSERT INTO premium_laptops (company, product, type_name, price_euros)
            SELECT company, product, type_name, price_euros
            FROM laptops
            WHERE price_euros > 500
        """
    )

    delete_laptops_table = SQLExecuteQueryOperator(
        task_id='delete_laptops_table',
        conn_id='postgres_connection_laptop_db',
        sql="""
            DELETE FROM laptops
        """
    )

    [create_laptops_table, create_premium_laptops_table] >> \
        wait_for_premium_laptops >> \
            insert_data_into_premium_laptops_table >> \
                delete_laptops_table
