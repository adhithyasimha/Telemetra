from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import time
import subprocess

def run_qualifying():
    subprocess.run(["python", "scripts/qualifying.py"])

def wait():
    time.sleep(5)

def run_race():
    subprocess.run(["python", "scripts/race_simulation.py"])

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
}

dag = DAG(
    'f1_simulation_dag',
    default_args=default_args,
    description='A DAG to simulate F1 qualifying and race sessions',
    schedule_interval='@daily',
)

qualifying_task = PythonOperator(
    task_id='run_qualifying',
    python_callable=run_qualifying,
    dag=dag,
)

wait_task = PythonOperator(
    task_id='wait',
    python_callable=wait,
    dag=dag,
)

race_task = PythonOperator(
    task_id='run_race',
    python_callable=run_race,
    dag=dag,
)

qualifying_task >> wait_task >> race_task