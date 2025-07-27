#!/bin/sh

echo "--- DEBUG: Starting run_gunicorn.sh ---"
echo "--- DEBUG: Current Working Directory: $(pwd) ---"
echo "--- DEBUG: PYTHONPATH: $PYTHONPATH ---"

# Verify that test_app.py exists and is readable in the current directory
echo "--- DEBUG: Listing files in current directory before Gunicorn ---"
ls -la .

# Attempt to directly import test_app as a Python module to see if that works outside Gunicorn
echo "--- DEBUG: Attempting a direct Python import of test_app ---"
python3 -c "import test_app; print('Direct import successful');" || { echo "Direct import failed!"; exit 1; }

# Run Gunicorn with verbose logging
echo "--- DEBUG: Executing Gunicorn command ---"
exec python3 -m gunicorn --bind 0.0.0.0:"$PORT" test_app:app --log-level debug --access-logfile - --error-logfile -
