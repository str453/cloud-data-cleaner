FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir gunicorn flask flask-cors PyJWT bcrypt mysql-connector-python
ENV PORT 8080
CMD ["gunicorn", "--bind", "0.0.0.0:$(PORT)", "main:app"]
