FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Copy all project files into the /app directory in the container
COPY . /app

# DEBUG: List contents of /app after copy to confirm files are there
RUN echo "--- DEBUG: Listing /app contents ---" && ls -la /app

# DEBUG: Show Python path before installing dependencies
RUN echo "--- DEBUG: PYTHONPATH before pip install ---" && echo $PYTHONPATH

# Install production dependencies.
RUN pip install --no-cache-dir gunicorn flask

# Set the Python path explicitly to include the current working directory
ENV PYTHONPATH=/app

# DEBUG: Show Python path after setting it
RUN echo "--- DEBUG: PYTHONPATH after setting ---" && echo $PYTHONPATH

ENV PORT 8080

# Explicitly run a Python script that then calls gunicorn
# This gives us more control over the environment Gunicorn sees
COPY run_gunicorn.sh /app/run_gunicorn.sh
RUN chmod +x /app/run_gunicorn.sh

# Use the shell script as the entrypoint
CMD ["/app/run_gunicorn.sh"]
