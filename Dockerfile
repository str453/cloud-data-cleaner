# Use the official Python image as a base.
# We're choosing Python 3.9 on a slim Debian Buster distribution for a smaller image size.
FROM python:3.9-slim-buster

# Set the working directory inside the container.
# All subsequent commands will be executed relative to this directory.
WORKDIR /app

# Copy the requirements.txt file into the container's working directory.
# This is done separately to leverage Docker's build cache. If only requirements.txt changes,
# the pip install step will be re-run; otherwise, it uses the cached layer.
COPY requirements.txt .

# Install the Python dependencies listed in requirements.txt.
# --no-cache-dir: Prevents pip from storing downloaded packages in a cache, saving space.
# -r requirements.txt: Installs packages from the specified file.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code (including main.py) into the container.
# The '.' indicates copying from the current build context (your repository root)
# to the current working directory inside the container (/app).
COPY . .

# Define the port that the container will listen on.
# Cloud Run injects the PORT environment variable, typically 8080.
# Setting ENV PORT 8080 here provides a default if PORT isn't set,
# and also informs Docker that the container intends to expose this port.
ENV PORT 8080 

# Command to run when the container starts.
# We use Gunicorn, a production-ready WSGI (Web Server Gateway Interface) server,
# to run the Flask application. This is more robust and performant than Flask's
# built-in development server (app.run()).
#
# --bind :$PORT: Binds Gunicorn to all network interfaces on the specified PORT.
# --workers 1: Number of worker processes. For Cloud Run, 1 worker is often sufficient.
# --threads 8: Number of threads per worker. Good for handling concurrent requests.
# main:app: Tells Gunicorn to find the 'app' Flask instance within the 'main.py' file.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
