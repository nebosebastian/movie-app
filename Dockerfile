# Use the official python image as a parent image
FROM python:3.9-slim

#Set thr working directory in thr container
WORKDIR / app

# Copy the requirments file into the container
COPY requirments.txt ,

# Intall the dependencies specified in the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current dirctory content into the container at /app
COPY . .

# Expose port 8000 to the host
EXPOSE 8000

# Command the run the FastAPI application using uvicorn
