from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ensure the src module is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger import logging
from src.exception import MyException
from src.components.model import ModelTraining
from src.config import CONFIG
import pandas as pd

def run_model_training():
    try:
        config = CONFIG["model_training"]

        X_train = pd.read_csv(config["TRAIN_FILE_NAME"])
        X_test = pd.read_csv(config["TEST_FILE_NAME"])
        y_train = pd.read_csv(config["TRAIN_LABEL_FILE_NAME"]) 
        y_test = pd.read_csv(config["TEST_LABEL_FILE_NAME"])

        logging.info(">>>>>Model Training Started...<<<<<")
        train = ModelTraining()
        train.handle_training(X_train, X_test, y_train, y_test)
        logging.info(">>>>>Model Training Completed<<<<<\n")

    except MyException as e:
        raise MyException(e, sys)

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Instantiate the DAG
with DAG(
    dag_id='model_training_pipeline',
    default_args=default_args,
    description='DAG for training ML model',
    schedule_interval=None,  # Run manually or trigger via API
    start_date=datetime(2025, 7, 1),
    catchup=False,
    tags=['ml', 'training'],
) as dag:

    training_task = PythonOperator(
        task_id='run_model_training',
        python_callable=run_model_training,
    )

    training_task
