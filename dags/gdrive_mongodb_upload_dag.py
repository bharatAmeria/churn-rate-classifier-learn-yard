from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))
from scripts import stage01_data_upload

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    dag_id='gdrive_mongodb_upload_pipeline',
    default_args=default_args,
    description='Run pipeline to download data from GDrive and upload to MongoDB',
    start_date=datetime(2025, 6, 27),
    schedule_interval='@daily',
    catchup=False
)

def run_data_upload_pipeline():
    stage01_data_upload.DataUploadPipeline.main()

run_pipeline_task = PythonOperator(
    task_id='run_data_upload_pipeline',
    python_callable=run_data_upload_pipeline,
    dag=dag
)
