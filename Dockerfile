FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . /app
RUN echo "--- DEBUG: Listing /app contents ---" && ls -la /app

# Added verbose output to pip install
RUN echo "--- DEBUG: Installing dependencies with pip ---" && \
    pip install --no-cache-dir -r requirements.txt --verbose && \
    echo "--- DEBUG: pip install complete ---"

# Add a step to list installed packages
RUN echo "--- DEBUG: Listing installed Python packages ---" && \
    pip freeze && \
    echo "--- DEBUG: End of installed Python packages ---"

ENV PORT 8080

# Command to run Gunicorn, explicitly targeting main.py and ensuring PYTHONPATH
CMD ["/bin/bash", "-c", "PYTHONPATH=/app python3 -m gunicorn --bind 0.0.0.0:$PORT main:app"]
