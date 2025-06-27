import os
import sys
import joblib
import pandas as pd
from src.config import CONFIG
from src.logger import logging
from src.exception import MyException
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble  import RandomForestClassifier
from sklearn.metrics import accuracy_score

class ModelTraining:

    def __init__(self):
        """Initialize the data ingestion class."""
        self.config = CONFIG["model_training"]
        logging.info("Model training class initialized.")

    def handle_training(self, X_train, X_test, y_train, y_test) -> None:

        try:
            
            models = {'lg':LogisticRegression(), 
                      'dtc':DecisionTreeClassifier(),
                      'rfc':RandomForestClassifier(),
                      }
            
            best_model_name = None
            best_model = None
            best_score = 0

            for name,model in models.items():
                model.fit(X_train, y_train)
                ypred = model.predict(X_test)
                acc = accuracy_score(y_test, ypred)
                print(f"{name} with accuracy : {acc} ")

                if acc > best_score:
                    best_score = acc
                    best_model_name = name
                    best_model = model

            print(f"\n✅ Best Model: {best_model_name} with Accuracy: {best_score}")

            best_model.fit(X_train, y_train)

            model_path = self.config["model"]
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(best_model ,open(model_path,'wb'))

        except Exception as e:
            logging.error("Error occurred while extracting zip file", exc_info=True)
            raise MyException(e, sys)


    # def prediction(credit_score,country,gender,age,tenure,balance,products_number,credit_card,active_member,estimated_salary):
    #         features = np.array([[credit_score,country,gender,age,tenure,balance,products_number,credit_card,active_member,estimated_salary]])
    #         features = sclr.fit_transform(features)
    #         prediction = rfc.predict(features).reshape(1,-1)
    #         return prediction[0]

    #         credit_score = 608
    #         country = 2
    #         gender = 0
    #         age= 41
    #         tenure= 1
    #         balance = 83807.86
    #         products_number= 1
    #         credit_card = 0
    #         active_member =1
    #         estimated_salary = 112542.58
