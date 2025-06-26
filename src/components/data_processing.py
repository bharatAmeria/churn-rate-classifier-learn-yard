import os
import sys
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
             df = data

             df.drop(['_id', 'customer_id'], axis=1)

             le = LabelEncoder()

             df['gender'] = le.fit_transform(df['gender'])
             df['country'] = le.fit_transform(df['country'])

             save_path = CONFIG["processed_data_path"]
             os.makedirs(os.path.dirname(save_path), exist_ok=True)
             df.to_csv(save_path, index=False)
             logging.info(f"Successfully saved processed data to {save_path}")

             self.df = df
             return df

        except Exception as e:
            logging.error("Error occurred in Processing data", exc_info=True)
            raise MyException(e, sys)
        
    def split_data_as_train_test(self) -> None:
        """
        Method Name :   split_data_as_train_test
        Description :   This method splits the dataframe into train set and test set based on split ratio 
        
        Output      :   Folder is created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        """
        logging.info("Entered split_data_as_train_test method of Data_Ingestion class")

        try:
            if self.df is None:
                raise ValueError("Data must be processed first using `handle_data()` before splitting.")

            X = self.df.drop(['_id', 'churn', 'customer_id'], axis=1)
            y = self.df.drop('_id', axis=1)
            y = self.df['churn']
            train_set, test_set, _, _ = train_test_split(X, y, test_size=self.config["TRAIN_TEST_SPLIT_RATIO"], random_state=42)
            logging.info("Performed train test split on the dataframe")
            logging.info("Exited split_data_as_train_test method of Data_Ingestion class")

            sclr = StandardScaler()
            X_train = sclr.fit_transform(train_set)
            X_test = sclr.fit_transform(test_set)

            dir_path = os.path.dirname(self.config["FILE_NAME"])
            os.makedirs(dir_path,exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")
            os.makedirs(os.path.dirname(self.config["TRAIN_FILE_NAME"]), exist_ok=True)
            pd.DataFrame(X_train).to_csv(self.config["TRAIN_FILE_NAME"], index=False)
            pd.DataFrame(X_test).to_csv(self.config["TEST_FILE_NAME"], index=False, header=True)

            logging.info(f"Exported train and test file path.")
        except Exception as e:
            raise MyException(e, sys)
        
