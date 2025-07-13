FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements and install them
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY app/app.py .
COPY app/model.pkl .
COPY app/templates ./templates

# Expose port FastAPI will use
EXPOSE 8050

# Start FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8050"]
