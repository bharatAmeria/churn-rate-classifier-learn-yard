# airflow/dags/data_upload_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from src.pipeline.stage01_data_upload import run_data_upload_pipeline

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='data_upload_pipeline_dag',
    default_args=default_args,
    description='DAG for uploading data from CSV to MongoDB',
    schedule_interval='@daily',
    catchup=False
) as dag:

    upload_data_task = PythonOperator(
        task_id='run_data_upload_pipeline',
        python_callable=run_data_upload_pipeline
    )

    upload_data_task
