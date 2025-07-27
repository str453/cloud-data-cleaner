FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . /app
RUN echo "--- DEBUG: Listing /app contents ---" && ls -la /app

# Install only Flask, no gunicorn for this test
RUN pip install --no-cache-dir flask

ENV PYTHONPATH=/app
ENV PORT 8080

# New CMD: Directly run the test_app.py using Flask's built-in server
CMD ["python3", "test_app.py"]
