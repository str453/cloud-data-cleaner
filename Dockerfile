FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Copy all project files into the /app directory in the container
COPY . /app

# Add a debug command to list files in the /app directory
# This will show up in your Cloud Build logs.
RUN ls -la /app

# Install production dependencies.
RUN pip install --no-cache-dir gunicorn flask flask-cors PyJWT bcrypt mysql-connector-python

# Set the Python path explicitly to include the current working directory
# This helps Python find modules in the current directory.
ENV PYTHONPATH=/app

# Define the port your application will listen on
ENV PORT 8080

# Run the web service on container startup using Gunicorn
# 'main:app' refers to the 'app' Flask instance within 'main.py'
CMD ["gunicorn", "--bind", "0.0.0.0:$(PORT)", "main:app"]
