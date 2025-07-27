# main.py
import os
import datetime
from functools import wraps
import jwt
import bcrypt
from flask import Flask, request, jsonify, g # Remove send_from_directory here as it implies static files which you generally don't serve from the backend
from flask_cors import CORS
import mysql.connector

# --- ONLY ONE Flask app instance, at the very top ---
app = Flask(__name__)
CORS(app, supports_credentials=True) # Apply CORS to the ONE app instance

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a_very_secure_random_key_that_is_at_least_32_chars_long')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

DB_USER = os.environ.get('DB_USER', 'your_db_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_db_password')
DB_NAME = os.environ.get('DB_NAME', 'csuf454')

DB_SOCKET_PATH = os.environ.get('DB_SOCKET_PATH')

# For local testing or external connections, use host and port.
DB_HOST = os.environ.get('DB_HOST', '34.169.250.193')
DB_PORT = os.environ.get('DB_PORT', 3306) # Correct default MySQL port

# --- REMOVE THESE UNNECESSARY ROUTES FOR A BACKEND-ONLY SERVICE ---
# If your frontend is serving favicon.ico and the root path, these are not needed.
# If you *do* need them for some reason, ensure they are part of the *single* app instance.

# from flask import send_from_directory # If you still need send_from_directory, import it here

# @app.route('/favicon.ico')
# def favicon():
#     # You would need to ensure app.static_folder is correctly configured or
#     # provide an absolute path to your favicon.
#     return send_from_directory(app.static_folder, 'favicon.ico')

# @app.route('/')
# def hello():
#     return 'Hello World!'

# --- IMPORTANT: REMOVE ALL app.run() CALLS FOR CLOUD RUN DEPLOYMENT WITH GUNICORN ---
# The 'if __name__ == "__main__":' block is typically for local development only.
# Gunicorn handles running your app on Cloud Run.
# If you *must* have it for local testing, ensure it's a single block.
# Example for local testing (only if you run 'python main.py' directly):
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 8080))
#     app.run(debug=True, host='0.0.0.0', port=port)

# ... (rest of your functions and API routes should remain as they are,
#      they all operate on the 'app' object defined at the very top)
