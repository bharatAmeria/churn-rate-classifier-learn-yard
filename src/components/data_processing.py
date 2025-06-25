import os
import sys
from abc import ABC, abstractmethod
from typing import Union
from src.config import CONFIG
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from src.logger import logging
from src.exception import MyException

class DataStrategy(ABC):
    """
    Abstract Class defining strategy for handling data
    """
    @abstractmethod
    def handle_data(self, data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
        pass

class DataPreprocessStrategy(DataStrategy):
    """
    Data preprocessing strategy which preprocesses the data.
    """
    def handle_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Removes columns which are not required, fills missing values with median average values,
        and converts the data type to float.
        """
        try:
             df = data
             df['Item_Weight'] = df['Item_Weight'].fillna(df['Item_Weight'].mean())
             df['Outlet_Size'].mode()

             mode_of_outlet_size = df.pivot_table(values='Outlet_Size',columns='Outlet_Type',aggfunc=lambda x: x.mode()[0])
             miss_values = df['Outlet_Size'].isnull()   
             df.loc[miss_values, 'Outlet_Size'] = df.loc[miss_values,'Outlet_Type'].apply(lambda x: mode_of_outlet_size[x])

             df.replace({'Item_Fat_Content': {'low fat':'Low Fat','LF':'Low Fat', 'reg':'Regular'}}, inplace=True)

             encoder = LabelEncoder()

             df['Item_Identifier'] = encoder.fit_transform(df['Item_Identifier'])
             df['Item_Fat_Content'] = encoder.fit_transform(df['Item_Fat_Content'])
             df['Item_Type'] = encoder.fit_transform(df['Item_Type'])
             df['Outlet_Identifier'] = encoder.fit_transform(df['Outlet_Identifier'])
             df['Outlet_Size'] = encoder.fit_transform(df['Outlet_Size'])
             df['Outlet_Location_Type'] = encoder.fit_transform(df['Outlet_Location_Type'])
             df['Outlet_Type'] = encoder.fit_transform(df['Outlet_Type'])

             save_path = CONFIG["processed_data_path"]
             os.makedirs(os.path.dirname(save_path), exist_ok=True)
             df.to_csv(save_path, index=False)
             logging.info(f"Successfully saved processed data to {save_path}")

        except Exception as e:
            logging.error("Error occurred in Processing data", exc_info=True)
            raise MyException(e, sys)
        
class DataPreProcessing(DataStrategy):
    """
    Data cleaning class which preprocesses the data
    """
    def __init__(self, data: pd.DataFrame, strategy: DataStrategy) -> None:
        """Initializes the DataCleaning class with a specific strategy."""
        logging.info("Initializing DataPreProcessing with given strategy")
        self.df = data
        self.strategy = strategy

    def handle_data(self) -> Union[pd.DataFrame, pd.Series]:
        """Handle data based on the provided strategy"""
        logging.info("Handling data using the provided strategy")
        return self.strategy.handle_data(self.df)
