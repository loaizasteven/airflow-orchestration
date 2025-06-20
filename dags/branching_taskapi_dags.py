from datetime import datetime
from airflow.decorators import dag, task
import pandas as pd

from airflow.operators.python import PythonOperator
from airflow.models import Variable

Variable.set(key='transform', value='filter_two_seaters')

from pathlib import Path

root_dir = Path(__file__).parents[1]

@dag(
    dag_id='branching_taskapi_dag',
    start_date=datetime.now(),
    schedule=None,
    tags=['python', 'airflow', 'taskapi', 'branching'],
)
def branching_taskapi_dag():

    def read_csv_file():
        df = pd.read_csv(root_dir / 'datasets' / 'car_data.csv')
        return df.to_json()

    @task.branch() # this task will return the task id of the task to be executed
    def determine_branch():
        final_output= Variable.get('transform', default_var=None)

        if final_output == 'filter_two_seaters':
            return 'filter_two_seaters_task'
        elif final_output == 'filter_fwds':
            return 'filter_fwds_task'
        
    def filter_two_seaters_task(ti):
        json_data = ti.xcom_pull(task_ids='read_csv_file_task')
        df = pd.read_json(json_data)

        # filter the dataframe
        two_seater_df = df[df['Seats'] == 2]

        # push the dataframe to the XComs
        ti.xcom_push(key='transformed_result', value=two_seater_df.to_json())
        ti.xcom_push(key='transform_filename', value='two_seaters')

    def filter_fwds_task(ti):
        json_data = ti.xcom_pull(task_ids='read_csv_file_task')
        df = pd.read_json(json_data)

        # filter the dataframe
        fwd_df = df[df['PowerTrain'] == 'FWD']

        # push the dataframe to the XComs
        ti.xcom_push(key='transformed_result', value=fwd_df.to_json())
        ti.xcom_push(key='transform_filename', value='fwds')

    def write_csv_results(ti):
        # Generic approach: try to pull from any upstream task that has the required XCom keys
        json_data = ti.xcom_pull(key='transformed_result')
        file_name = ti.xcom_pull(key='transform_filename')
        
        # If the generic pull didn't work, try all upstream tasks explicitly
        if json_data is None or file_name is None:
            upstream_task_ids = ti.task.upstream_task_ids
            
            for task_id in upstream_task_ids:
                if json_data is None:
                    json_data = ti.xcom_pull(task_ids=task_id, key='transformed_result')
                if file_name is None:
                    file_name = ti.xcom_pull(task_ids=task_id, key='transform_filename')
                
                # If we found both pieces of data, we can stop
                if json_data is not None and file_name is not None:
                    print(f"Found data from task: {task_id}")
                    break
        
        # Final error check
        if json_data is None:
            raise ValueError("No transformed_result found in any upstream task")
        if file_name is None:
            raise ValueError("No transform_filename found in any upstream task")

        df = pd.read_json(json_data)
        df.to_csv(root_dir / 'output' / f'{file_name}.csv', index=False)

    read_csv_file_task = PythonOperator(
        task_id='read_csv_file_task',
        python_callable=read_csv_file,
    )

    filter_two_seaters_task = PythonOperator(
        task_id='filter_two_seaters_task',
        python_callable=filter_two_seaters_task,
    )

    filter_fwds_task = PythonOperator(
        task_id='filter_fwds_task',
        python_callable=filter_fwds_task,
    )

    write_csv_results_task = PythonOperator(
        task_id='write_csv_results_task',
        python_callable=write_csv_results,
        trigger_rule='none_failed_min_one_success', # Runs if at least one upstream task succeeds and none fail
    )

    read_csv_file_task >> determine_branch() >> [filter_two_seaters_task, filter_fwds_task] >> write_csv_results_task

branching_taskapi_dag()
