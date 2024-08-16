# Use a base image
FROM python:3.12

# Install MySQL development libraries
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential

# Set up your working directory
WORKDIR /app

# Copy your requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose port and run your application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
