FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . /app
RUN echo "--- DEBUG: Listing /app contents ---" && ls -la /app

RUN pip install --no-cache-dir gunicorn flask

ENV PYTHONPATH=/app
ENV PORT 8080

COPY run_gunicorn.sh /app/run_gunicorn.sh
RUN chmod +x /app/run_gunicorn.sh

CMD ["/app/run_gunicorn.sh"] # Make sure this line is present
