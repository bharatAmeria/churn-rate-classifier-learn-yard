FROM apache/airflow:2.6.3

# Copy requirements
COPY requirements.txt /

# Official way to install Python packages
RUN bash -c "pip install --user --no-cache-dir -r /requirements.txt"

# Set PYTHONPATH to include DAGs directory so 'scripts' is importable
ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow/dags"