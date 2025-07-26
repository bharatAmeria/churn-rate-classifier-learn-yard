import sys
import pandas as pd
from src.constants import *
from src.components.data_upload import UploadData
from src.logger import logging
from src.exception import MyException

class DataUploadPipeline:
    def __init__(self):
        pass

    @staticmethod
    def main():
        upload = UploadData()
        upload.download_file()
        upload.extract_zip_file()
        df = pd.read_csv("artifacts/Bank Customer Churn Prediction.csv")

        # Call the function
        inserted = upload.push_dataframe_to_mongodb(df, "Churn_rate", "Churn_Data")
        print(f"{len(inserted)} documents inserted.")



if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {INGESTION_STAGE_NAME} started <<<<<<")
        obj = DataUploadPipeline()
        obj.main()
    except MyException as e:
            raise MyException(e, sys)