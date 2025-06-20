import os
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task
import pandas as pd

# NOTE: Connection 'my_prod_database' should be created via CLI or UI
# Connection created via CLI: airflow connections add 'my_prod_database' --conn-type sqlite --conn-host '/path/to/db'git


root_dir = Path(__file__).parents[1]

default_args = {
    'owner': 'airflow_sql',
    'start_date': datetime(2025, 1, 1),
    'depends_on_past': False,
    'retries': 0,
}

@dag(
    dag_id='sqllite_taskapi_dag',
    default_args=default_args,
    schedule=None,
    tags=['python', 'airflow', 'taskapi', 'sqlite'],
)
def data_transformation_storage_pipeline():
    @task
    def read_dataset():
        df = pd.read_csv(root_dir / 'datasets' / 'car_data.csv')
        return df.to_json()

    @task
    def create_sqlite_table():
        from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
        from airflow.providers.sqlite.hooks.sqlite import SqliteHook
        
        hook = SqliteHook(sqlite_conn_id='my_prod_database')
        hook.run(sql="""
        CREATE TABLE IF NOT EXISTS car_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            body_style INTEGER NOT NULL,
            seat INTEGER NOT NULL,
            price INTEGER NOT NULL
        );
        """)
    
    @task
    def write_to_database(**kwargs):
        from airflow.providers.sqlite.hooks.sqlite import SqliteHook
        
        ti = kwargs['ti']
        json_data = ti.xcom_pull(task_ids='read_dataset')

        df = pd.read_json(json_data)
        df = df[['Brand', 'Model', 'BodyStyle', 'Seats', 'Price']]
        df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)

        insert_query = """
            INSERT INTO car_data (brand, model, body_style, seat, price)
            VALUES (?,?,?,?,?)
        """

        # Use the SQLite hook from the provider
        hook = SqliteHook(sqlite_conn_id='my_prod_database')
        
        parameters = df.to_dict(orient='records')
        for record in parameters:
            hook.run(sql=insert_query, parameters=tuple(record.values()))

    read_dataset() >> create_sqlite_table() >> write_to_database()

data_transformation_storage_pipeline()
