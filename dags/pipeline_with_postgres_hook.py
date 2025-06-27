from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook  
from airflow.models import Variable

from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0
}

employees_table = Variable.get('emp', default_var='employees')
departments_table = Variable.get('dept', default_var='departments')
employees_departments_table = Variable.get('emp_dept', default_var='employees_departments')

def create_employees_table():
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {employees_table} (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        age INTEGER NOT NULL,
        department_id INT NOT NULL
    )"""
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def create_departments_table():
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {departments_table} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL
    )"""

    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def insert_data_employees(employees: list):
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')
    
    insert_data_query = f"""
    INSERT INTO {employees_table} (first_name, last_name, age, department_id)
    VALUES (%s, %s, %s, %s)
    """

    conn = hook.get_conn()
    cursor = conn.cursor()
    
    for employee in employees:
        first_name, last_name, age, department_id = employee
        cursor.execute(insert_data_query, (first_name, last_name, age, department_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def insert_data_departments(departments: list):
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')
    
    insert_data_query = f"""
    INSERT INTO {departments_table} (name)
    VALUES (%s)
    """

    conn = hook.get_conn()
    cursor = conn.cursor()
    
    for department in departments:
        cursor.execute(insert_data_query, (department,))
    
    conn.commit()
    cursor.close()
    conn.close()

def join_table():
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')

    join_table_query = f"""
    CREATE TABLE IF NOT EXISTS {employees_departments_table} AS
    SELECT 
        employees.first_name,
        employees.last_name,
        employees.age,
        departments.name as department_name
    FROM {employees_table} employees
    JOIN {departments_table} departments ON employees.department_id = departments.id
    """

    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(join_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def display_emp_dept():
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')

    retrieve_results_query = f"""
    SELECT * FROM {employees_departments_table}
    """

    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(retrieve_results_query)
    results = cursor.fetchall()

    for row in results:
        print(row)

    cursor.close()
    conn.close()
    
def filtering_join_table(condition: str):
    hook = PostgresHook(postgres_conn_id='postgres_connection_organization_db')

    filtering_join_table_query = f"""
    SELECT * FROM {employees_departments_table}
    WHERE {condition}
    """

    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(filtering_join_table_query)
    results = cursor.fetchall()

    for row in results:
        print(row)

    cursor.close()
    conn.close()

with DAG(
    dag_id='pipelnie_with_postgres_hook',
    description='A pipeline with a Postgres hook',
    default_args=default_args,
    start_date=datetime(2025, 6, 26),
    schedule='@once',
    tags=['postgres', 'pipeline', 'hooks'],
) as dag:

    create_employees_table_task = PythonOperator(
        task_id='create_employees_table',
        python_callable=create_employees_table,
    )

    create_departments_table_task = PythonOperator(
        task_id='create_departments_table',
        python_callable=create_departments_table,
    )

    employees = [
        ('John', 'Doe', 30, 1),
        ('Jane', 'Smith', 25, 2),
        ('Jim', 'Beam', 35, 3),
        ('Peter', 'Parker', 28, 1),
        ('Mary', 'Jane', 22, 2),
        ('Tony', 'Stark', 40, 3),
        ('Bruce', 'Wayne', 32, 1),
        ('Clark', 'Kent', 31, 2),
        ('Diana', 'Prince', 29, 3),
        ('Barry', 'Allen', 27, 1),
    ]

    insert_data_employees_task = PythonOperator(
        task_id='insert_data_employees',
        python_callable=insert_data_employees,
        op_kwargs={'employees': employees},
    )   

    departments = ['Engineering', 'Sales', 'Marketing']

    insert_data_departments_task = PythonOperator(
        task_id='insert_data_departments',
        python_callable=insert_data_departments,
        op_kwargs={'departments': departments},
    )

    join_table_task = PythonOperator(
        task_id='join_table',
        python_callable=join_table,
    )

    display_emp_dept_task = PythonOperator(
        task_id='display_emp_dept',
        python_callable=display_emp_dept,
    )

    filtering_join_table_task = PythonOperator(
        task_id='filtering_join_table',
        python_callable=filtering_join_table,
        op_kwargs={'condition': "age > 30"},
    )

    create_employees_table_task >> insert_data_employees_task >> \
        join_table_task >> display_emp_dept_task >> \
            filtering_join_table_task

    create_departments_table_task >> insert_data_departments_task >> \
        join_table_task >> display_emp_dept_task >> \
            filtering_join_table_task