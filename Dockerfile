# Use the official Python image as a base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container at /app
COPY . .

# Expose the port that the application will listen on
# Cloud Run expects the application to listen on the port specified by the PORT environment variable.
ENV PORT 8080
EXPOSE $PORT

# Run the application using Gunicorn
# 'main:app' refers to the 'app' Flask instance within 'main.py'
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
