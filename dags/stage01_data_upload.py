from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import sys
import pandas as pd
from src.constants import *
from src.components.data_upload import UploadData
from src.logger import logging
from src.exception import MyException

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

def run_data_upload_pipeline():
    try:
        logging.info(f">>>>>> stage {INGESTION_STAGE_NAME} started <<<<<<")
        upload = UploadData()
        upload.download_file()
        upload.extract_zip_file()

        df = pd.read_csv("artifacts/Bank Customer Churn Prediction.csv")
        inserted = upload.push_dataframe_to_mongodb(df, "Proj1", "Proj1-Data")
        logging.info(f"{len(inserted)} documents inserted to MongoDB.")
    except Exception as e:
        raise MyException(e, sys)

with DAG(
    dag_id='data_upload_pipeline_dag',
    default_args=default_args,
    description='Upload data to MongoDB from CSV',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['data_ingestion'],
) as dag:

    run_pipeline = PythonOperator(
        task_id='run_data_upload_pipeline',
        python_callable=run_data_upload_pipeline,
    )

    run_pipeline
