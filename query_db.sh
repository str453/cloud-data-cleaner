#!/bin/bash

# --- Configuration Variables ---
# IMPORTANT: Replace these with your actual Cloud SQL instance details
PROJECT_ID="454password"        # Your Google Cloud Project ID
REGION="us-west1"           # E.g., us-west1, us-central1
INSTANCE_NAME="csuf454"      # The name of your Cloud SQL instance (e.g., my-cipher-db)
DB_NAME="csuf454"                       # The database name you've set (already changed to csuf454)
DB_USER="csuf454"                  # Your Cloud SQL database user (e.g., root, or a custom user)

# Construct the full connection name
CONNECTION_NAME="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"

# --- Step 1: Connect to the database and open a MySQL/PostgreSQL client ---
# This command will prompt you for your DB_USER's password.
# Once connected, you'll be inside the database client (e.g., mysql> or postgres=#)
# You can then type SQL queries directly.
echo "Attempting to connect to Cloud SQL instance: ${CONNECTION_NAME}"
echo "Using database: ${DB_NAME} with user: ${DB_USER}"
echo "You will be prompted for the database user's password."
gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --database="${DB_NAME}"

# --- Once connected, you can run SQL commands like these directly in the client: ---

# To show all tables in your 'csuf454' database:
# SHOW TABLES;

# To see the schema (structure) of the 'users' table:
# DESCRIBE users;  # For MySQL
# \d users;      # For PostgreSQL

# To see the schema (structure) of the 'files' table:
# DESCRIBE files;  # For MySQL
# \d files;      # For PostgreSQL

# --- Example SQL queries you can run AFTER connecting ---

# Insert a sample user (replace with actual email and a hashed password)
# Note: In a real scenario, you'd hash the password in your backend.
# For testing here, you can insert a plain email, but the password_hash should be a bcrypt hash.
# INSERT INTO users (email, password_hash) VALUES ('test@example.com', '$2b$12$EXAMPLEHASHFORPASSWORD');

# Insert a sample file (assuming user_id 1 exists from the above insert)
# INSERT INTO files (user_id, file_name, cipher_type, content, save_type)
# VALUES (1, 'sample_encrypted.csv', 'caesar', 'encrypted_csv_content_here', 'private');

# Select all users:
# SELECT * FROM users;

# Select all files:
# SELECT * FROM files;

# Select private files for a specific user_id (e.g., user_id 1):
# SELECT * FROM files WHERE user_id = 1 AND save_type = 'private';

# Select public files:
# SELECT * FROM files WHERE save_type = 'public';

# Delete a specific file (replace 123 with an actual file ID):
# DELETE FROM files WHERE id = 123;

# --- To exit the database client, type: ---
# exit;

# --- Step 2: (Optional) Run a single SQL query directly from bash ---
# This is useful for quick checks without opening the interactive client.
# Replace "SELECT VERSION();" with your desired SQL query.
# Note: This will still prompt for the password.
echo -e "\n--- Running a single SQL query (e.g., SELECT VERSION()) ---"
gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --database="${DB_NAME}" --quiet --batch --execute="SELECT VERSION();"

# Example: Get all users without interactive prompt (requires password)
# echo -e "\n--- Getting all users ---"
# gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --database="${DB_NAME}" --quiet --batch --execute="SELECT id, email FROM users;"

# Example: Get all files (requires password)
# echo -e "\n--- Getting all files ---"
# gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --database="${DB_NAME}" --quiet --batch --execute="SELECT id, user_id, file_name, cipher_type, save_type FROM files;"
