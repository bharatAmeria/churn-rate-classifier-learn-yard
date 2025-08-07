from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.constants import *
from src.logger import logging
from src.exception import MyException
from src.components.data_upload import UploadData
from src.components.dataIngestion import IngestData
from src.components.data_processing import DataPreprocess
from src.components.model import ModelTraining
from src.config import CONFIG

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def run_data_upload_pipeline():
    try:
        logging.info(f">>>>>> Stage: {INGESTION_STAGE_NAME} started <<<<<<")
        upload = UploadData()
        upload.download_file()
        upload.extract_zip_file()

        df = pd.read_csv("artifacts/Bank Customer Churn Prediction.csv")
        inserted = upload.push_dataframe_to_mongodb(df, "Proj1", "Proj1-Data")
        logging.info(f"{len(inserted)} documents inserted to MongoDB.")
    except Exception as e:
        raise MyException(e, sys)

def run_data_ingestion_pipeline():
    try:
        logging.info(f"*******************")
        logging.info(f">>>>>> Stage: {PRE_PROCESSING_STAGE_NAME} started <<<<<<")
        ingestor = IngestData()
        ingestor.initiate_data_ingestion()
        logging.info(f">>>>>> Stage: {PRE_PROCESSING_STAGE_NAME} completed <<<<<<\nx==========x")
    except Exception as e:
        raise MyException(e, sys)

def run_data_processing_pipeline():
    try:
        logging.info("*******************")
        logging.info(f">>>>>> Stage: {PRE_PROCESSING_STAGE_NAME} started <<<<<<")

        config = CONFIG["data_ingest"]
        data = pd.read_csv(config["feature_store"])

        logging.info(">>>>> Data Preprocessing Started... <<<<<")
        data_cleaning = DataPreprocess()
        data_cleaning.handle_data(data=data)
        data_cleaning.split_data_as_train_test()
        logging.info(">>>>> Data Preprocessing Completed <<<<<")

        logging.info(f">>>>>> Stage: {PRE_PROCESSING_STAGE_NAME} completed <<<<<<\nx==========x")

    except Exception as e:
        raise MyException(e, sys)

def run_model_training():
    try:
        config = CONFIG["model_training"]

        X_train = pd.read_csv(config["TRAIN_FILE_NAME"])
        X_test = pd.read_csv(config["TEST_FILE_NAME"])
        y_train = pd.read_csv(config["TRAIN_LABEL_FILE_NAME"]) 
        y_test = pd.read_csv(config["TEST_LABEL_FILE_NAME"])

        logging.info(">>>>> Model Training Started... <<<<<")
        train = ModelTraining()
        train.handle_training(X_train, X_test, y_train, y_test)
        logging.info(">>>>> Model Training Completed <<<<<")

    except MyException as e:
        raise MyException(e, sys)

with DAG(
    dag_id='end_to_end_ml_pipeline',
    default_args=default_args,
    description='Full ML pipeline: upload → ingest → preprocess → train',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'end_to_end'],
) as dag:

    upload_task = PythonOperator(
        task_id='data_upload',
        python_callable=run_data_upload_pipeline,
    )

    ingestion_task = PythonOperator(
        task_id='data_ingestion',
        python_callable=run_data_ingestion_pipeline,
    )

    processing_task = PythonOperator(
        task_id='data_processing',
        python_callable=run_data_processing_pipeline,
    )

    training_task = PythonOperator(
        task_id='model_training',
        python_callable=run_model_training,
    )

    # Set sequential dependencies
    upload_task >> ingestion_task >> processing_task >> training_task
