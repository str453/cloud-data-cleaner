import os
import datetime
from functools import wraps
import jwt # PyJWT library
import bcrypt # For password hashing
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
import mysql.connector

print("--- DEBUG: Starting main.py execution ---")

app = Flask(__name__)
CORS(app, supports_credentials=True)

print("--- DEBUG: Flask app initialized ---")

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a_very_secure_random_key_that_is_at_least_32_chars_long')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600

DB_USER = os.environ.get('DB_USER', 'csuf454')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'csuf')
DB_NAME = os.environ.get('DB_NAME', 'csuf454')

# Corrected: Use CLOUD_SQL_CONNECTION_NAME provided by Cloud Run
CLOUD_SQL_CONNECTION_NAME = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

# For local testing or external connections
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 3306)

print("--- DEBUG: Environment variables processed ---")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)

print("--- DEBUG: After if __name__ block (gunicorn will run app) ---")

def get_db_connection():
    """Establishes a connection to the Cloud SQL database."""
    try:
        # --- CRITICAL CHANGE HERE ---
        # If CLOUD_SQL_CONNECTION_NAME is set, use the Unix socket connection
        if CLOUD_SQL_CONNECTION_NAME:
            unix_socket_path = f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"
            print(f"--- DEBUG: Attempting DB connection via Unix socket: {unix_socket_path} ---")
            conn = mysql.connector.connect(
                unix_socket=unix_socket_path,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else:
            # Fallback for local development or if Cloud SQL proxy isn't used
            print(f"--- DEBUG: CLOUD_SQL_CONNECTION_NAME not set, attempting to connect via host/port: {DB_HOST}:{DB_PORT} ---")
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        print("--- DEBUG: DB connection successful! ---")
        return conn
    except mysql.connector.Error as err:
        print(f"--- DEBUG ERROR: Database connection error in get_db_connection: {err} ---")
        raise
    except Exception as e:
        print(f"--- DEBUG ERROR: Unexpected error in get_db_connection: {e} ---")
        raise

# ... (rest of your Flask routes and functions remain the same) ...

print("--- DEBUG: End of main.py file execution ---")
