#!/bin/sh

# Direct all echoes to stdout/stderr
echo "--- DEBUG: Starting run_gunicorn.sh (direct output) ---"
echo "--- DEBUG: Current Working Directory: $(pwd) ---"
echo "--- DEBUG: PYTHONPATH: $PYTHONPATH ---"

echo "--- DEBUG: Listing files in current directory before Gunicorn ---"
ls -la .

# Attempt to directly import test_app as a Python module to see if that works outside Gunicorn
# This will print success/failure to stdout/stderr directly
echo "--- DEBUG: Attempting a direct Python import of test_app ---"
python3 -c "import test_app; print('Direct import successful');" || { echo "Direct import failed! Exiting..."; exit 1; }

echo "--- DEBUG: Executing Gunicorn command directly to stdout/stderr ---"

# Execute Gunicorn. The 'exec' command replaces the current shell process with Gunicorn,
# ensuring Gunicorn's stdout/stderr is the primary output of the container.
# --log-level debug is critical for verbosity.
# --access-logfile - and --error-logfile - ensure logs go to stdout/stderr.
exec python3 -m gunicorn --bind 0.0.0.0:"$PORT" test_app:app --log-level debug --access-logfile - --error-logfile -
