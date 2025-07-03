import os
import sys
from pandas import DataFrame
import mlflow
from datetime import datetime
from src.logger import logging
from src.exception import MyException
from src.config import CONFIG
from src.data_fetch.bank_churn_data import Proj1Data


class IngestData:
    """
    Data ingestion class which ingests data from the source and returns a DataFrame.
    """

    def __init__(self):
        """Initialize the data ingestion class."""
        self.config = CONFIG["data_ingest"]
        logging.info("Data Ingestion class initialized.")

    def export_data_into_feature_store(self):
        """
        Export data from MongoDB to a CSV file and return it as a DataFrame.
        Logs parameters and artifact with MLflow.
        """
        try:
            logging.info(f"Exporting data from MongoDB")

            my_data = Proj1Data()
            dataframe = my_data.export_collection_as_dataframe()

            rows, cols = dataframe.shape
            mlflow.log_param("feature_store_rows", rows)
            mlflow.log_param("feature_store_cols", cols)

            logging.info(f"Shape of dataframe: {dataframe.shape}")

            feature_store_file_path = self.config["feature_store"]
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info(f"Saving exported data to: {feature_store_file_path}")
            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            mlflow.log_param("feature_store_path", feature_store_file_path)
            mlflow.log_artifact(feature_store_file_path, artifact_path="feature_store")

            return dataframe

        except Exception as e:
            mlflow.log_param("feature_store_export", "failed")
            raise MyException(e, sys)

    def initiate_data_ingestion(self):
        """
        Orchestrate the data ingestion step. 
        Logs overall process under a single MLflow run.
        """
        logging.info("Entered initiate_data_ingestion method of IngestData class")

        try:
            with mlflow.start_run(run_name="DataIngestion_" + datetime.now().strftime("%Y%m%d_%H%M%S")):
                mlflow.log_param("ingestion_stage", "start")
                
                dataframe = self.export_data_into_feature_store()
                mlflow.log_param("ingestion_status", "success")

                logging.info("Got the data from MongoDB")
                logging.info("Exited initiate_data_ingestion method of IngestData class")

        except Exception as e:
            mlflow.log_param("ingestion_status", "failed")
            raise MyException(e, sys)
