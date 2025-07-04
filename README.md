# 📊 Customer Churn Prediction Pipeline

This project demonstrates a **production-ready, end-to-end Machine Learning pipeline** to predict whether a customer is likely to churn. Built with **Apache Airflow**, **Docker**, and exposed via a **REST API**, the architecture is modular, scalable, and reproducible.

---

## 🚀 Project Overview

* **Objective:** Predict customer churn based on historical behavioral data.
* **Pipeline Highlights:**

  * Orchestrated with **Apache Airflow DAGs**
  * **Dockerized** components for reproducibility
  * Deployed using **Docker Compose**
  * Distinct stages: data ingestion → transformation → training → evaluation → packaging
  * Real-time inference through a **REST API**

---

## 🛠️ Tools & Technologies

### 🌀 Apache Airflow

* **Purpose:** Workflow orchestration of ETL and ML tasks.
* **How:** How: DAGs manage and link pipeline stages. In this project, Airflow is responsible for ingesting multiple raw CSV files over time from Google Drive, triggering the data processing pipeline after each ingestion. Once the data is cleaned and prepared, it's passed downstream for model training.
  
### 🐳 Docker

* **Purpose:** Environment consistency across development, testing, and production.
* **How:** Each pipeline stage runs in its own container.

### 🧹 Docker Compose

* **Purpose:** Simplifies multi-container orchestration.
* **How:** Spins up Airflow, pipeline services, and the REST API.

### ⚡ REST API (FastAPI / Flask)

* **Purpose:** Exposes a `/predict` endpoint for real-time inference.
* **How:** Loads serialized ML model and processes incoming data.

### 🐍 Python

* **Purpose:** Core language for ML, data preprocessing, and deployment.
* **How:** Powers each task script and the API backend.

---

## ✅ Key Benefits

* Modular and maintainable architecture.
* Easily deployable across environments.
* Clean separation of concerns.
* Real-time prediction ready via REST API.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/customer-churn-ml.git
cd customer-churn-ml
```

## 2️⃣ Environment Setup (Optional but Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate           # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

🔍 **Alternative:**  
Run the `testEnvironment.py` file to automatically set up the virtual environment and install dependencies.

🛠 Modify `setup.py` and `pyproject.toml` to reflect your author and project information.

---

## 3️⃣ Data Ingestion Pipeline

1. **Download Raw Data:**
   - Data is fetched from **Google Drive** and unzipped.

2. **Push to MongoDB:**
   - Extracted raw data is uploaded to **MongoDB Atlas**.

3. **Data Processing:**
   - Data is retrieved from MongoDB for processing and cleaning.

4. **Train-Test Split:**
   - Cleaned data is split into training and testing sets.

📂 All related scripts are available in `src/components/`.

---

## 4️⃣ MongoDB Atlas Setup

1. **Sign Up** at [mongodb.com](https://www.mongodb.com).
2. **Create Organization**  
   ![Mongo Organisation](assets/org.png)

3. **Create a New Project**  
   ![New Project](assets/proj.png)

4. **Build a Free Cluster**  
   ![Project Home](assets/cluster.png)

5. **Configure Cluster (Default Settings)**  
   ![Cluster Building](assets/cluster_making.png)

6. **Access Cluster Home Page**  
   ![Cluster Home](assets/cluster_home.png)

7. **Connect Application:**
   - Click `Connect` → Choose `Drivers` → Copy the connection string.
   - Save it in `.env` as:
     ```env
     MONGO_URI="your_mongo_connection_string"
     ```

---

## 5️⃣ Run with Docker Compose

```bash
docker-compose up --build
```

### 🔗 Access Services:

- **Airflow UI:** [http://localhost:8080](http://localhost:8080)  
- **API Endpoint (FastAPI):** [http://localhost:8000/predict](http://localhost:8000/predict)

---

## ⚙️ Manual Airflow Setup (Optional)

> 💡 Only needed if you're not using Docker Compose.

```bash
# Get the official Docker Compose file for Airflow
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.2/docker-compose.yaml'

# Set up project directories
mkdir -p ./dags ./logs ./plugins

# Create .env file with user ID
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Initialize Airflow metadata database
docker compose up airflow-init
```

### 🔐 Airflow Login Credentials

- **Username:** `airflow`  
- **Password:** `airflow`

#### Login Interface  
![Airflow Login](assets/airflow_login_page.png)

#### Airflow Dashboard  
![Airflow Home](assets/airflow_home_page.png)

---

## 📬 Contact

For queries, feedback, or contributions:

👤 [Bharat Aameriya](https://www.linkedin.com/in/bharat-aameriya-24579a261/)  
📂 Feel free to open an issue or submit a pull request on this repository.

---
