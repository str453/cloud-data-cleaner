ENV PORT 8080 
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
