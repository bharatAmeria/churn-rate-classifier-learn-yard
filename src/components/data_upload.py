import os
import sys
import zipfile
import certifi
import gdown
import pymongo
from dotenv import load_dotenv
from src.logger import logging
from src.exception import MyException
from src.config import CONFIG
import mlflow
from src.constants import *
from datetime import datetime

load_dotenv()

class UploadData:
    """
    Data ingestion class which ingests data from the source and returns a DataFrame.
    """
    
    def __init__(self):
        """Initialize the data ingestion class."""
        self.config = CONFIG["data_upload"]
        
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
    
    def download_file(self):
        """Fetch data from the URL"""
        try:
            mlflow.set_experiment("Upload Data")
            with mlflow.start_run(run_name="DownloadFile_" + datetime.now().strftime("%Y%m%d_%H%M%S")):
                
                dataset_url = self.config["source_URL"]
                zip_download_dir = self.config["local_data_file"]
                
                # Ensure the directory exists
                os.makedirs("artifacts/data", exist_ok=True)
                
                logging.info(f"Downloading data from {dataset_url} into file {zip_download_dir}")
                
                # Extract file ID and download
                file_id = dataset_url.split("/")[-2]
                prefix = 'https://drive.google.com/uc?/export=download&id='
                gdown.download(prefix + file_id, zip_download_dir)
                
                # Log parameters
                mlflow.log_param("dataset_url", dataset_url)
                mlflow.log_param("download_status", "success")
                
                # Try to log artifact with error handling
                try:
                    if os.path.exists(zip_download_dir):
                        mlflow.log_artifact(zip_download_dir, artifact_path="downloads")
                        logging.info("Successfully logged artifact to MLflow")
                except PermissionError as pe:
                    logging.warning(f"Could not log artifact to MLflow due to permission error: {pe}")
                except Exception as ae:
                    logging.warning(f"Could not log artifact to MLflow: {ae}")
                
                logging.info(f"Successfully downloaded data from {dataset_url} into file {zip_download_dir}")
                
        except Exception as e:
            logging.error("Error occurred while downloading file", exc_info=True)
            try:
                mlflow.log_param("download_status", "failed")
            except:
                pass
            raise MyException(e, sys)
    
    def extract_zip_file(self):
        """
        Extracts the zip file into the data directory
        """
        try:
            mlflow.set_experiment("Upload Data")
            with mlflow.start_run(run_name="ExtractZipFile_" + datetime.now().strftime("%Y%m%d_%H%M%S")):

                unzip_path = self.config["unzip_dir"]
                local_data_file = self.config["local_data_file"]
                
                # Ensure the directory exists
                os.makedirs(unzip_path, exist_ok=True)
                
                logging.info(f"Extracting zip file {local_data_file} to {unzip_path}")
                
                with zipfile.ZipFile(local_data_file, 'r') as zip_ref:
                    zip_ref.extractall(unzip_path)
                
                # Log parameters
                mlflow.log_param("extract_status", "success")
                
                # Try to log artifact with error handling
                try:
                    if os.path.exists(unzip_path):
                        mlflow.log_artifact(unzip_path, artifact_path="extracted")
                        logging.info("Successfully logged extracted files to MLflow")
                except PermissionError as pe:
                    logging.warning(f"Could not log extracted files to MLflow due to permission error: {pe}")
                except Exception as ae:
                    logging.warning(f"Could not log extracted files to MLflow: {ae}")
                
                logging.info(f"Successfully extracted zip file to {unzip_path}")
                
        except Exception as e:
            logging.error("Error occurred while extracting zip file", exc_info=True)
            try:
                mlflow.log_param("extract_status", "failed")
            except:
                pass
            raise MyException(e, sys)
    
    def push_dataframe_to_mongodb(self, df, DATABASE_NAME, COLLECTION_NAME):
        """
        Push a pandas DataFrame to MongoDB using connection string from .env.
        
        Parameters:
        df (pd.DataFrame): Data to upload
        db_name (str): MongoDB database name
        collection_name (str): Collection name inside the database
        
        Returns:
        inserted_ids (list): List of inserted document IDs
        """
        client = None
        try:
            mlflow.set_experiment("Upload Data")
            with mlflow.start_run(run_name="PushDataframeToMongoDB_" + datetime.now().strftime("%Y%m%d_%H%M%S")):

                # Convert DataFrame to dictionary records
                data = df.to_dict(orient='records')
                
                # Get MongoDB connection string
                connection_url = os.getenv("MONGODB_URI")
                if not connection_url:
                    raise ValueError("MONGODB_URI not found in environment variables")
                
                # Connect to MongoDB
                client = pymongo.MongoClient(connection_url, tlsCAFile=certifi.where())
                database = client[DATABASE_NAME]
                collection = database[COLLECTION_NAME]
                
                # Insert data
                result = collection.insert_many(data)
                
                # Log success parameters
                try:
                    mlflow.log_param("mongodb_collection", COLLECTION_NAME)
                    mlflow.log_param("records_inserted", len(result.inserted_ids))
                    mlflow.log_param("mongodb_upload_status", "success")
                    mlflow.log_param("database_name", DATABASE_NAME)
                except Exception as me:
                    logging.warning(f"Could not log MongoDB parameters to MLflow: {me}")
                
                logging.info(f"Successfully inserted {len(result.inserted_ids)} records into {DATABASE_NAME}.{COLLECTION_NAME}")
                return result.inserted_ids
            
        except Exception as e:
            logging.error(f"Error occurred while pushing data to MongoDB: {e}", exc_info=True)
            try:
                mlflow.log_param("mongodb_upload_status", "failed")
            except:
                pass
            raise MyException(e, sys)
        
        finally:
            # Close MongoDB connection
            if client:
                try:
                    client.close()
                except:
                    pass
    
    def __del__(self):
        """Cleanup method to ensure MLflow run is ended."""
        try:
            if hasattr(self, 'mlflow_run') and self.mlflow_run:
                mlflow.end_run()
        except:
            pass