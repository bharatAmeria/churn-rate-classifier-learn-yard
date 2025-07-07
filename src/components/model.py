import os
import sys
import joblib
import mlflow
import mlflow.sklearn
from datetime import datetime
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
        """Initialize the model training class."""
        self.config = CONFIG["model_training"]
        logging.info("Model training class initialized.")

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


    def handle_training(self, X_train, X_test, y_train, y_test) -> None:
        try:
            mlflow.set_experiment("Churn-Model-Training")

            models = {
                'lg': LogisticRegression(),
                'dtc': DecisionTreeClassifier(),
                'rfc': RandomForestClassifier(),
            }

            best_model_name = None
            best_model = None
            best_score = 0.0

            for name, model in models.items():
                with mlflow.start_run(run_name=f"train_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    acc = accuracy_score(y_test, y_pred)

                    print(f"{name} with accuracy: {acc}")
                    logging.info(f"{name} accuracy: {acc}")

                    mlflow.log_param("model_name", name)
                    mlflow.log_metric("accuracy", acc)

                    if acc > best_score:
                        best_score = acc
                        best_model_name = name
                        best_model = model

            logging.info(f"\n✅ Best Model: {best_model_name} with Accuracy: {best_score}")
            logging.info(f"Best Model: {best_model_name} with Accuracy: {best_score}")

            # Retrain best model
            best_model.fit(X_train, y_train)

            model_path = self.config["model"]
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(best_model, open(model_path, 'wb'))
            logging.info(f"Saved best model to {model_path}")

            # Log best model in MLflow
            with mlflow.start_run(run_name=f"best_model_{best_model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                mlflow.log_param("best_model", best_model_name)
                mlflow.log_metric("best_accuracy", best_score)
                mlflow.log_artifact(model_path, artifact_path="models")
                mlflow.sklearn.log_model(sk_model=best_model, artifact_path="sk_model")
                
        except MyException as e:
            logging.error("Error occurred during model training", exc_info=True)
            mlflow.log_param("training_status", "failed")
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
