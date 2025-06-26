import sys
from src.logger import logging
from src.exception import MyException
from src.components.dataIngestion import IngestData
from src.constants import *

class DataProcessingPipeline:
    def __init__(self):
        pass

    @staticmethod
    def main():
        ingestor = IngestData()
        ingestor.initiate_data_ingestion()
        df = ingestor.export_data_into_feature_store()

        return df


if __name__ == '__main__':
    try:
        logging.info(f"*******************")
        logging.info(f">>>>>> stage {PRE_PROCESSING_STAGE_NAME} started <<<<<<")
        obj = DataProcessingPipeline()
        obj.main()
        logging.info(f">>>>>> stage {PRE_PROCESSING_STAGE_NAME} completed <<<<<<\nx==========x")
    except MyException as e:
            raise MyException(e, sys)
