from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import sys
import pandas as pd
from src.constants import *
from src.config import CONFIG
from src.logger import logging
from src.exception import MyException
from src.components.data_processing import DataPreprocess

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

def run_data_processing_pipeline():
    try:
        logging.info("*******************")
        logging.info(f">>>>>> stage {PRE_PROCESSING_STAGE_NAME} started <<<<<<")

        config = CONFIG["data_ingest"]
        data = pd.read_csv(config["feature_store"])

        logging.info(">>>>>Data Preprocessing Started...<<<<<")
        data_cleaning = DataPreprocess()
        data_cleaning.handle_data(data=data)
        data_cleaning.split_data_as_train_test()
        logging.info(">>>>>Data Preprocessing Completed<<<<<\n")

        logging.info(f">>>>>> stage {PRE_PROCESSING_STAGE_NAME} completed <<<<<<\nx==========x")

    except Exception as e:
        raise MyException(e, sys)

with DAG(
    dag_id='data_processing_pipeline_dag',
    default_args=default_args,
    description='Data preprocessing DAG: clean, validate, split data',
    schedule_interval=None,  # Change as needed
    start_date=days_ago(1),
    catchup=False,
    tags=['data_processing'],
) as dag:

    run_processing = PythonOperator(
        task_id='run_data_processing',
        python_callable=run_data_processing_pipeline,
    )

    run_processing
