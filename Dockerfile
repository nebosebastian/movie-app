# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install system dependencies for mysqlclient (if you need mysqlclient)
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    pkg-config \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory
COPY app /app/app

# Set environment variables
ENV PYTHONPATH=/app/app

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
