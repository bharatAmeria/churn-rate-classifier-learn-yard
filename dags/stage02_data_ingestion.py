from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import sys
from src.logger import logging
from src.exception import MyException
from src.components.dataIngestion import IngestData
from src.constants import *

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

def run_data_ingestion_pipeline():
    try:
        logging.info(f"*******************")
        logging.info(f">>>>>> stage {PRE_PROCESSING_STAGE_NAME} started <<<<<<")
        ingestor = IngestData()
        ingestor.initiate_data_ingestion()
        logging.info(f">>>>>> stage {PRE_PROCESSING_STAGE_NAME} completed <<<<<<\nx==========x")
    except Exception as e:
        raise MyException(e, sys)

with DAG(
    dag_id='data_ingestion_pipeline_dag',
    default_args=default_args,
    description='Ingest raw data for pipeline',
    schedule_interval=None,  # You can change to '@daily' etc. if needed
    start_date=days_ago(1),
    catchup=False,
    tags=['data_ingestion'],
) as dag:

    run_ingestion = PythonOperator(
        task_id='run_data_ingestion',
        python_callable=run_data_ingestion_pipeline,
    )

    run_ingestion
