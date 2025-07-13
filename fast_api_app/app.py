from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from joblib import load
import numpy as np
from sklearn.preprocessing import StandardScaler

app = FastAPI()
templates = Jinja2Templates(directory="templates")

model = load("model.pkl")
scaler = StandardScaler() 

# For JSON POST requests
class CustomerData(BaseModel):
    credit_score: float
    country: str
    gender: str
    age: float
    tenure: float
    balance: float
    products_number: float
    credit_card: float
    active_member: float
    estimated_salary: float

country_map = {"France": 0, "Spain": 1, "Germany": 2}
gender_map = {"Female": 0, "Male": 1}


def preprocess(data):
    try:
        country = country_map[data['country']]
        gender = gender_map[data['gender']]
    except KeyError as e:
        raise ValueError(f"Invalid value: {e}")

    features = np.array([[data['credit_score'], country, gender, data['age'],
                          data['tenure'], data['balance'], data['products_number'],
                          data['credit_card'], data['active_member'], data['estimated_salary']]])
    
    features_scaled = scaler.fit_transform(features)  # Use `.transform()` with trained scaler
    return features_scaled


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/predict-form", response_class=HTMLResponse)
async def predict_form(
    request: Request,
    credit_score: float = Form(...),
    country: str = Form(...),
    gender: str = Form(...),
    age: float = Form(...),
    tenure: float = Form(...),
    balance: float = Form(...),
    products_number: float = Form(...),
    credit_card: float = Form(...),
    active_member: float = Form(...),
    estimated_salary: float = Form(...)
):
    try:
        data = {
            "credit_score": credit_score,
            "country": country,
            "gender": gender,
            "age": age,
            "tenure": tenure,
            "balance": balance,
            "products_number": products_number,
            "credit_card": credit_card,
            "active_member": active_member,
            "estimated_salary": estimated_salary
        }

        features = preprocess(data)
        prediction = model.predict(features)[0]
        message = "Customer has left." if prediction == 1 else "Customer is still active."
        return templates.TemplateResponse("form.html", {"request": request, "result": message})

    except Exception as e:
        return templates.TemplateResponse("form.html", {"request": request, "result": str(e)})
