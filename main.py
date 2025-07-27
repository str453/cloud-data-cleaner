import os
import datetime
from functools import wraps
import jwt # PyJWT library
import bcrypt # For password hashing
# Corrected: Combine both Flask imports into one line
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
import mysql.connector

print("--- DEBUG: Starting main.py execution ---") # Add this

# --- ONLY ONE Flask app instance, at the very top ---
app = Flask(__name__)
CORS(app, supports_credentials=True) # Enable CORS for frontend communication

print("--- DEBUG: Flask app initialized ---") # Add this

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'a_very_secure_random_key_that_is_at_least_32_chars_long')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600 # Token expires in 1 hour

DB_USER = os.environ.get('DB_USER', 'csuf454') # Make sure this is 'csuf454' or your actual DB user
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'csuf') # Make sure this is 'csuf' or your actual DB password
DB_NAME = os.environ.get('DB_NAME', 'csuf454') # Make sure this is 'csuf454' or your actual DB name

DB_SOCKET_PATH = os.environ.get('DB_SOCKET_PATH')

# For local testing or external connections, use host and port.
# Cloud Run will use DB_SOCKET_PATH when --add-cloudsql-instances is set.
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1') # Default for local
DB_PORT = os.environ.get('DB_PORT', 3306) # Standard MySQL port

print("--- DEBUG: Environment variables processed ---") # Add this


# --- IMPORTANT: This block is ONLY for local development ---
if __name__ == '__main__':
    # Cloud Run provides a PORT environment variable. Listen on it.
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)

# Place this print statement *outside* the if __name__ == "__main__": block
print("--- DEBUG: After if __name__ block (gunicorn will run app) ---") # Add this

def get_db_connection():
    """Establishes a connection to the Cloud SQL database."""
    try:
        print(f"--- DEBUG: Attempting DB connection. DB_SOCKET_PATH: {DB_SOCKET_PATH} ---") # Add this
        if DB_SOCKET_PATH:
            conn = mysql.connector.connect(
                unix_socket=DB_SOCKET_PATH,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else:
            # This path should ideally NOT be hit in Cloud Run if Cloud SQL proxy is configured
            print(f"--- DEBUG: DB_SOCKET_PATH not set, attempting to connect via host/port: {DB_HOST}:{DB_PORT} ---") # Add this
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        print("--- DEBUG: DB connection successful! ---") # Add this
        return conn
    except mysql.connector.Error as err:
        print(f"--- DEBUG ERROR: Database connection error in get_db_connection: {err} ---") # Add this
        raise # Important: Re-raise so Cloud Run sees the crash
    except Exception as e:
        print(f"--- DEBUG ERROR: Unexpected error in get_db_connection: {e} ---") # Add this
        raise


def token_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            g.user_id = data['user_id']
            g.username = data['username'] # Attach username to global context
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token error: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials', 'message': 'Username and password are required'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "Conflict", "message": "Username already exists"}), 409

        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except mysql.connector.Error as err:
        print(f"Error registering user: {err}")
        # Check for duplicate entry error specifically (e.g., MySQL error code 1062)
        if err.errno == 1062: # Duplicate entry for unique key
            return jsonify({"error": "Conflict", "message": "Username already exists"}), 409
        return jsonify({'error': 'Database error', 'message': f'Failed to register user: {err}'}), 500
    except Exception as e:
        print(f"Unexpected error during registration: {e}")
        return jsonify({'error': 'Server error', 'message': f'Failed to register user: {e}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials', 'message': 'Username and password are required'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            token_payload = {
                'user_id': user['user_id'],
                'username': username, # Include username in token payload
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return jsonify({'message': 'Login successful', 'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials', 'message': 'Invalid username or password'}), 401
    except mysql.connector.Error as err:
        print(f"Error logging in: {err}")
        return jsonify({'error': 'Database error', 'message': f'Login failed due to DB error: {err}'}), 500
    except Exception as e:
        print(f"Unexpected error during login: {e}")
        return jsonify({'error': 'Server error', 'message': f'Login failed: {e}'}), 500
    finally:
        if conn:
            conn.close()


@app.route('/save_file', methods=['POST'])
@token_required
def save_file():
    user_id = g.user_id # From token_required decorator
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    save_type = data.get('save_type', 'private') # 'private' or 'public'

    if not filename or not content:
        return jsonify({"error": "Missing data", "message": "Filename and content are required"}), 400
    
    if save_type not in ['private', 'public']:
        return jsonify({"error": "Invalid data", "message": "Save type must be 'private' or 'public'"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (user_id, filename, content, save_type) VALUES (%s, %s, %s, %s)",
                       (user_id, filename, content, save_type))
        conn.commit()
        return jsonify({"message": "File saved successfully"}), 201
    except mysql.connector.Error as err:
        print(f"Error saving file: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to save file: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file save: {e}")
        return jsonify({"error": "Server error", "message": f"Failed to save file: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/get_files', methods=['GET'])
@token_required
def get_files():
    user_id = g.user_id
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Fetch private files for the user and all public files
        query = "SELECT id, filename, save_type, created_at FROM files WHERE user_id = %s OR save_type = 'public' ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        files = cursor.fetchall()
        return jsonify(files), 200
    except mysql.connector.Error as err:
        print(f"Error fetching files: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to fetch files: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file fetch: {e}")
        return jsonify({"error": "Server error", "message": f"Failed to fetch files: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/get_file_content/<int:file_id>', methods=['GET'])
@token_required
def get_file_content(file_id):
    user_id = g.user_id
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT user_id, content, save_type FROM files WHERE id = %s"
        cursor.execute(query, (file_id,))
        file_data = cursor.fetchone()

        if not file_data:
            return jsonify({"error": "Not Found", "message": "File not found"}), 404

        # Check permissions: if private, only owner can view; if public, anyone can view
        if file_data['save_type'] == 'private' and file_data['user_id'] != user_id:
            return jsonify({"error": "Forbidden", "message": "You do not have permission to view this private file"}), 403

        return jsonify({"content": file_data['content']}), 200
    except mysql.connector.Error as err:
        print(f"Error fetching file content: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to fetch file content: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file content fetch: {e}")
        return jsonify({"error": "Server error", "message": f"Failed to fetch file content: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/delete_file/<int:file_id>', methods=['DELETE'])
@token_required
def delete_file(file_id):
    user_id = g.user_id
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, check the file's ownership and save_type
        check_query = "SELECT user_id, save_type FROM files WHERE id = %s"
        cursor.execute(check_query, (file_id,))
        file_info = cursor.fetchone()

        if not file_info:
            return jsonify({"error": "Not Found", "message": "File not found"}), 404

        owner_id, save_type = file_info

        # Permission check: Only owner can delete private files. Public files can be deleted by owner.
        if save_type == 'private' and owner_id != user_id:
            return jsonify({"error": "Forbidden", "message": "You do not have permission to delete this private file"}), 403
        
        # If it's a public file, only the owner can delete it.
        if save_type == 'public' and owner_id != user_id:
            return jsonify({"error": "Forbidden", "message": "You do not have permission to delete this public file"}), 403

        delete_query = "DELETE FROM files WHERE id = %s"
        cursor.execute(delete_query, (file_id,))
        conn.commit()

        if cursor.rowcount == 0:
            # This case might be hit if the file was found but deleted by another process
            # or if permissions logic above wasn't comprehensive enough.
            return jsonify({"error": "Not Found", "message": "File not found or no permission"}), 404
        
        return jsonify({"message": "File deleted successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error deleting file from DB: {err}")
        return jsonify({"error": "Database error", "message": f"Failed to delete file: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during file deletion: {e}")
        return jsonify({"error": "Server error", "message": f"Failed to delete file: {e}"}), 500
    finally:
        if conn:
            conn.close()


print("--- DEBUG: End of main.py file execution ---") # Add this
