# main.py
import os
import datetime
from functools import wraps
import jwt # PyJWT library
import bcrypt # For password hashing
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import mysql.connector

# --- ONLY ONE Flask app instance ---
app = Flask(__name__)
CORS(app, supports_credentials=True) # Enable CORS for frontend communication

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a_very_secure_random_key_that_is_at_least_32_chars_long')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600 # Token expires in 1 hour

DB_USER = os.environ.get('DB_USER', 'your_db_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_db_password')
DB_NAME = os.environ.get('DB_NAME', 'csuf454')

DB_SOCKET_PATH = os.environ.get('DB_SOCKET_PATH')

# For local testing or external connections, use host and port.
# Ensure DB_PORT is set to the MySQL default if connecting directly via host/port
DB_HOST = os.environ.get('DB_HOST', '34.169.250.193')
DB_PORT = os.environ.get('DB_PORT', 3306) # MySQL default port is 3306

# --- REMOVE OR COMMENT OUT THESE FRONTEND-SPECIFIC ROUTES ---
# If your favicon.ico and other static files are handled by the frontend (Cloud Storage)
# @app.route('/favicon.ico')
# def favicon():
#    return send_from_directory(app.static_folder, 'favicon.ico')

# @app.route('/')
# def hello():
#    return 'Hello World!'

# --- The if __name__ == '__main__': block is ONLY for local development ---
# When deployed with Gunicorn, this block is typically not executed
# as Gunicorn imports 'app' directly.
if __name__ == '__main__':
    # Use the PORT environment variable provided by Cloud Run, default to 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)


def get_db_connection():
    """Establishes a connection to the Cloud SQL database."""
    try:
        if DB_SOCKET_PATH: # Use Unix socket if path is provided (for Cloud Run/App Engine)
            conn = mysql.connector.connect(
                unix_socket=DB_SOCKET_PATH,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else: # Fallback to host/port for local testing or external connections
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=int(DB_PORT), # Ensure DB_PORT is an integer
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def token_required(f):
    """Decorator to protect API endpoints, verifying JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"error": "Unauthorized", "message": "Authentication token is missing!"}), 401

        try:
            # Decode the token using the secret key and algorithm
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            # Attach user_id from the token payload to Flask's global request context (g)
            g.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Unauthorized", "message": "Authentication token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Unauthorized", "message": "Invalid authentication token"}), 401
        except Exception as e:
            print(f"Token decoding error: {e}")
            return jsonify({"error": "Unauthorized", "message": "Authentication token processing error"}), 401
        
        return f(*args, **kwargs)
    return decorated

# --- API Endpoints ---

@app.route('/health_check', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Cipher backend is running!"}), 200

@app.route('/register', methods=['POST'])
def register_user():
    """Registers a new user with username (email) and password."""
    data = request.get_json()
    username = data.get('username') # This is the email
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing credentials", "message": "Username (email) and password are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database error", "message": "Could not connect to database"}), 500

    try:
        cursor = conn.cursor()
        
        # Hash the password using bcrypt
        # bcrypt requires bytes, so encode password and decode hash
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Check if username (email) already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Conflict", "message": "Username (email) already exists"}), 409

        # Insert new user into the 'users' table
        query = "INSERT INTO users (email, password_hash) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        conn.commit()

        # After successful registration, log them in immediately and return a token
        # Get the ID of the newly created user
        user_id = cursor.lastrowid
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        return jsonify({"message": "User registered and logged in successfully", "token": token, "user_id": user_id}), 201
    except mysql.connector.Error as err:
        print(f"Error registering user: {err}")
        if err.errno == 1062: # MySQL error code for duplicate entry
            return jsonify({"error": "Conflict", "message": "Username (email) already exists"}), 409
        return jsonify({"error": "Database error", "message": f"Failed to register user: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during registration: {e}")
        return jsonify({"error": "Server error", "message": f"An unexpected error occurred: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login_user():
    """Logs in a user and returns a JWT."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing credentials", "message": "Username (email) and password are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database error", "message": "Could not connect to database"}), 500

    try:
        cursor = conn.cursor(dictionary=True) # Return results as dictionaries
        cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (username,))
        user = cursor.fetchone()

        # Verify user exists and password matches
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Password matches, generate JWT
            payload = {
                'user_id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return jsonify({"message": "Login successful", "token": token, "user_id": user['id']}), 200
        else:
            return jsonify({"error": "Unauthorized", "message": "Invalid username or password"}), 401
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": "Server error", "message": f"An error occurred during login: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/save_file', methods=['POST'])
@token_required # Protect this endpoint with JWT verification
def save_file():
    """Saves a processed file to Cloud SQL."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request", "message": "No JSON data provided"}), 400

    file_name = data.get('fileName')
    cipher_type = data.get('cipherType')
    content = data.get('content')
    save_type = data.get('saveType') # 'private' or 'public'

    if not all([file_name, cipher_type, content, save_type]):
        return jsonify({"error": "Missing data", "message": "Required fields: fileName, cipherType, content, saveType"}), 400

    if save_type not in ['private', 'public']:
        return jsonify({"error": "Invalid save type", "message": "saveType must be 'private' or 'public'"}), 400

    # Get user_id from the authenticated request context (set by @token_required)
    user_id = g.user_id

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database error", "message": "Could not connect to database"}), 500

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO files (user_id, file_name, cipher_type, content, save_type, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, file_name, cipher_type, content, save_type, datetime.datetime.now()))
        conn.commit()
        return jsonify({"message": "File saved successfully", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        print(f"Error saving file to DB: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to save file: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file save: {e}")
        return jsonify({"error": "Server error", "message": f"An unexpected error occurred: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/get_files', methods=['GET'])
@token_required # Protect this endpoint
def get_files():
    """Retrieves saved files for the authenticated user and public files."""
    user_id = g.user_id # From authenticated request context

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database error", "message": "Could not connect to database"}), 500

    try:
        cursor = conn.cursor(dictionary=True) # Return results as dictionaries

        private_query = "SELECT id, file_name, cipher_type, save_type, content, timestamp FROM files WHERE user_id = %s AND save_type = 'private'"
        cursor.execute(private_query, (user_id,))
        private_files = cursor.fetchall()

        public_query = "SELECT id, file_name, cipher_type, save_type, content, timestamp FROM files WHERE save_type = 'public'"
        cursor.execute(public_query)
        public_files = cursor.fetchall()

        all_files = private_files + public_files
        
        for file_data in all_files:
            if isinstance(file_data.get('timestamp'), datetime.datetime):
                file_data['timestamp'] = file_data['timestamp'].isoformat()

        return jsonify({"files": all_files}), 200
    except mysql.connector.Error as err:
        print(f"Error retrieving files from DB: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to retrieve files: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file retrieval: {e}")
        return jsonify({"error": "Server error", "message": f"An unexpected error occurred: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/delete_file/<int:file_id>', methods=['DELETE'])
@token_required # Protect this endpoint
def delete_file(file_id):
    """Deletes a file, ensuring the user owns it or it's a public file."""
    user_id = g.user_id # From authenticated request context

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database error", "message": "Could not connect to database"}), 500

    try:
        cursor = conn.cursor()

        check_query = "SELECT user_id, save_type FROM files WHERE id = %s"
        cursor.execute(check_query, (file_id,))
        file_info = cursor.fetchone()

        if not file_info:
            return jsonify({"error": "Not Found", "message": "File not found"}), 404

        owner_id, save_type = file_info

        
        if save_type == 'private' and owner_id != user_id:
            return jsonify({"error": "Forbidden", "message": "You do not have permission to delete this private file"}), 403
        
        delete_query = "DELETE FROM files WHERE id = %s"
        cursor.execute(delete_query, (file_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Not Found", "message": "File not found or no permission"}), 404
        
        return jsonify({"message": "File deleted successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error deleting file from DB: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to delete file: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file deletion: {e}")
        return jsonify({"error": "Server error", "message": f"An unexpected error occurred: {e}"}), 500
    finally:
        if conn:
            conn.close()
