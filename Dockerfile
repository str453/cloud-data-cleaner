# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim-buster

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
WORKDIR /app
COPY . /app

# Install production dependencies.
# This assumes you have a requirements.txt file in your project root.
RUN pip install --no-cache-dir gunicorn flask flask-cors PyJWT bcrypt mysql-connector-python

# Port to listen on.
# This should match the port Gunicorn is configured to bind to.
# Cloud Run will set the PORT environment variable.
ENV PORT 8080

# Run the web service on container startup.
# The `main:app` part refers to:
#   - `main`: The Python module (your main.py file)
#   - `app`: The Flask application instance (app = Flask(__name__))
CMD ["gunicorn", "--bind", "0.0.0.0:$(PORT)", "main:app"]
