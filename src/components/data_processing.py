import os
import sys
import mlflow
from datetime import datetime
from src.config import CONFIG
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from src.logger import logging
from src.exception import MyException
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class DataPreprocess:
    """
    Data preprocessing strategy which preprocesses the data.
    """

    def __init__(self):
        """Initialize the data ingestion class."""
        self.config = CONFIG["data_ingest"]
        self.df = None
        logging.info("Data Processing class initialized.")

    def handle_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Removes columns which are not required, fills missing values with median average values,
        and converts the data type to float.
        """
        try:
            mlflow.set_experiment("Churn-Preprocessing")
            with mlflow.start_run(run_name="HandleData_" + datetime.now().strftime("%Y%m%d_%H%M%S")):

                df = data.copy()
                mlflow.log_param("initial_shape", df.shape)

                df.drop(['_id', 'customer_id'], axis=1, inplace=True)

                le = LabelEncoder()
                df['gender'] = le.fit_transform(df['gender'])
                df['country'] = le.fit_transform(df['country'])

                save_path = CONFIG["processed_data_path"]
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                df.to_csv(save_path, index=False)

                mlflow.log_param("columns_encoded", ['gender', 'country'])
                mlflow.log_param("processed_shape", df.shape)
                mlflow.log_artifact(save_path, artifact_path="processed_data")

                logging.info(f"Successfully saved processed data to {save_path}")

                self.df = df
                return df

        except Exception as e:
            logging.error("Error occurred in Processing data", exc_info=True)
            mlflow.log_param("processing_status", "failed")
            raise MyException(e, sys)

    def split_data_as_train_test(self) -> None:
        """
        Splits the dataframe into train/test and scales features.
        Saves the split files and logs them with MLflow.
        """
        logging.info("Entered split_data_as_train_test method of DataPreprocess class")
        try:
            if self.df is None:
                raise ValueError("Data must be processed first using `handle_data()` before splitting.")

            mlflow.set_experiment("Churn-Preprocessing")
            with mlflow.start_run(run_name="SplitData_" + datetime.now().strftime("%Y%m%d_%H%M%S")):

                X = self.df.drop(['churn'], axis=1)
                y = self.df['churn']

                train_set, test_set, y_train, y_test = train_test_split(
                    X, y,
                    test_size=self.config["TRAIN_TEST_SPLIT_RATIO"],
                    random_state=42
                )

                mlflow.log_param("split_ratio", self.config["TRAIN_TEST_SPLIT_RATIO"])
                mlflow.log_param("X_train_shape", train_set.shape)
                mlflow.log_param("X_test_shape", test_set.shape)

                sclr = StandardScaler()
                X_train = sclr.fit_transform(train_set)
                X_test = sclr.transform(test_set)

                os.makedirs(os.path.dirname(self.config["FILE_NAME"]), exist_ok=True)
                os.makedirs(os.path.dirname(self.config["TRAIN_FILE_NAME"]), exist_ok=True)

                pd.DataFrame(X_train).to_csv(self.config["TRAIN_FILE_NAME"], index=False)
                pd.DataFrame(X_test).to_csv(self.config["TEST_FILE_NAME"], index=False, header=True)
                pd.DataFrame(y_train).to_csv(self.config["TRAIN_LABEL_FILE_NAME"], index=False)
                pd.DataFrame(y_test).to_csv(self.config["TEST_LABEL_FILE_NAME"], index=False)

                mlflow.log_artifact(self.config["TRAIN_FILE_NAME"], artifact_path="split")
                mlflow.log_artifact(self.config["TEST_FILE_NAME"], artifact_path="split")
                mlflow.log_artifact(self.config["TRAIN_LABEL_FILE_NAME"], artifact_path="split")
                mlflow.log_artifact(self.config["TEST_LABEL_FILE_NAME"], artifact_path="split")

                logging.info("Exported train and test file paths.")

        except Exception as e:
            mlflow.log_param("split_status", "failed")
            raise MyException(e, sys)
    