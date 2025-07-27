FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . /app
RUN echo "--- DEBUG: Listing /app contents ---" && ls -la /app

# Install both gunicorn and flask
RUN pip install --no-cache-dir gunicorn flask

ENV PORT 8080

# New CMD: Explicitly set PYTHONPATH directly in the Gunicorn command.
# We use a shell command to ensure variable expansion and proper path handling.
CMD ["/bin/bash", "-c", "PYTHONPATH=/app python3 -m gunicorn --bind 0.0.0.0:$PORT test_app:app"]
