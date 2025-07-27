FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app
# Copy all project files into the /app directory in the container
COPY . /app

# Install your actual dependencies from requirements.txt, plus gunicorn
RUN pip install --no-cache-dir gunicorn flask

ENV PORT 8080

# Command to run Gunicorn, explicitly targeting main.py and ensuring PYTHONPATH
# This assumes your Flask app instance in main.py is named 'app'.
CMD ["/bin/bash", "-c", "PYTHONPATH=/app python3 -m gunicorn --bind 0.0.0.0:$PORT main:app"]
