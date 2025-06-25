import os
import sys
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from src.config import CONFIG
from sklearn.model_selection import train_test_split
from sklearn import metrics
from typing import Union
from abc import ABC, abstractmethod
from src.logger import logging
from src.exception import MyException

class ModelTrainingStrategy(ABC):

    @abstractmethod
    def handle_training(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

class ModelTrainingConfig(ModelTrainingStrategy):

    def handle_training(self, data: pd.DataFrame) -> pd.DataFrame:

        try:
            df = data

            X = df.drop(columns='Item_Outlet_Sales', axis=1)
            y = df['Item_Outlet_Sales']

            X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.2, random_state=2)

            regressor = XGBRegressor()
            regressor.fit(X_train,Y_train)
            y_pred = regressor.predict(X_test)

            print(metrics.r2_score(Y_test, y_pred))

            # input = (250,6.89,1,0.136428,13,193.9820,8,1997,2,0,1)
            # new_input = np.asanyarray(input,dtype=float)
            # prediciton = regressor.predict(new_input.reshape(1,-1))
            # print(prediciton)

            model_path = CONFIG["model"]
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(regressor,open(model_path,'wb'))

        except Exception as e:
            logging.error("Error occurred while extracting zip file", exc_info=True)
            raise MyException(e, sys)

class ModelTraining(ModelTrainingStrategy):
    def __init__(self, data: pd.DataFrame, strategy: ModelTrainingStrategy):
        self.strategy = strategy
        self.df = data

    def handle_training(self) -> Union[pd.DataFrame, pd.Series]:
        """Handle data based on the provided strategy"""
        return self.strategy.handle_training(self.df)
