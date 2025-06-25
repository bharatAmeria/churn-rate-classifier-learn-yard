import sys

from src.constants import *
from src.components.dataIngestion import IngestData
from src.logger import logging
from src.exception import MyException

class DataIngestionTrainingPipeline:
    def __init__(self):
        pass

    @staticmethod
    def main():
        data_ingestion = IngestData()
        data_ingestion.download_file()
        data_ingestion.extract_zip_file()


if __name__ == '__main__':
    try:
        logging.info(f">>>>>> stage {INGESTION_STAGE_NAME} started <<<<<<")
        obj = DataIngestionTrainingPipeline()
        obj.main()
    except MyException as e:
            raise MyException(e, sys)