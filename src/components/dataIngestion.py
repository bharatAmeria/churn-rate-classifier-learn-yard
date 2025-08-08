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

    @staticmethod
    def setup_dagshub_mlflow(repo_owner: str, repo_name: str, dagshub_token: str):
        """
        Sets up MLflow to track experiments using DagsHub.
        
        Args:
            repo_owner (str): DagsHub repository owner (username or organization).
            repo_name (str): DagsHub repository name.
            dagshub_token (str): Personal access token for DagsHub.

        Raises:
            EnvironmentError: If the dagshub_token is not provided.
        """
        try: 
            if not dagshub_token:
                raise EnvironmentError("DAGSHUB_TOKEN is not provided.")

            os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
            os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

            dagshub_url = f"https://dagshub.com/{repo_owner}/{repo_name}.mlflow"
            os.environ["MLFLOW_TRACKING_URI"] = dagshub_url

            logging.info(f"MLflow tracking URI set to: {dagshub_url}")
        except MyException as e:
            logging.info(f"Unexpected error while setting up MLflow tracking: {e}")
            raise MyException(e, sys)

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
                
                self.export_data_into_feature_store()
                mlflow.log_param("ingestion_status", "success")

                logging.info("Got the data from MongoDB")
                logging.info("Exited initiate_data_ingestion method of IngestData class")

        except Exception as e:
            mlflow.log_param("ingestion_status", "failed")
            raise MyException(e, sys)
 
    def __del__(self):
        """Cleanup method to ensure MLflow run is ended."""
        try:
            if hasattr(self, 'mlflow_run') and self.mlflow_run:
                mlflow.end_run()
        except:
            pass