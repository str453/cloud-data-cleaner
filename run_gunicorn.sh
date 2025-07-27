#!/bin/sh

LOG_FILE="/tmp/gunicorn_startup.log" # Define a log file path

echo "--- DEBUG: Starting run_gunicorn.sh ---" >> "$LOG_FILE" 2>&1
echo "--- DEBUG: Current Working Directory: $(pwd) ---" >> "$LOG_FILE" 2>&1
echo "--- DEBUG: PYTHONPATH: $PYTHONPATH ---" >> "$LOG_FILE" 2>&1

echo "--- DEBUG: Listing files in current directory before Gunicorn ---" >> "$LOG_FILE" 2>&1
ls -la . >> "$LOG_FILE" 2>&1

echo "--- DEBUG: Attempting a direct Python import of test_app ---" >> "$LOG_FILE" 2>&1
python3 -c "import test_app; print('Direct import successful');" >> "$LOG_FILE" 2>&1 || { echo "Direct import failed!" >> "$LOG_FILE" 2>&1; exit 1; }

echo "--- DEBUG: Executing Gunicorn command ---" >> "$LOG_FILE" 2>&1

# Run Gunicorn, pipe its output to the log file, and also to stdout
exec python3 -m gunicorn --bind 0.0.0.0:"$PORT" test_app:app --log-level debug --access-logfile - --error-logfile - >> "$LOG_FILE" 2>&1 &

# Give Gunicorn a moment to start and write some logs
sleep 5

echo "--- DEBUG: Content of gunicorn_startup.log ---"
cat "$LOG_FILE"
echo "--- DEBUG: End of gunicorn_startup.log ---"

# Keep the script running so the container doesn't exit immediately
# This might help capture more logs if the crash is delayed
wait # Wait for Gunicorn to exit (it should if it crashes)
