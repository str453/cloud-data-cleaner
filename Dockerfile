FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . /app
RUN ls -la /app # Keep this for debugging, output will be in Cloud Build logs

# Install only necessary packages for the minimal app
RUN pip install --no-cache-dir gunicorn flask

ENV PYTHONPATH=/app # Still good to include this
ENV PORT 8080

# This CMD now points to 'test_app:app' from the 'test_app.py' file
CMD ["python3", "-m", "gunicorn", "--bind", "0.0.0.0:$(PORT)", "test_app:app"]
