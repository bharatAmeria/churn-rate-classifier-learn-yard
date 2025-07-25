FROM quay.io/astronomer/astro-runtime:12.1.1

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN touch /usr/local/airflow/.project-root