#!/bin/bash

# --- Configuration Variables ---
# IMPORTANT: Replace these with your actual Cloud SQL instance details
PROJECT_ID="forward-scion-465216-s9"     # Your Google Cloud Project ID from the screenshot
REGION="us-west1"                       # Your instance region from the screenshot
INSTANCE_NAME="454password"             # The name of your Cloud SQL instance from the screenshot
DB_NAME="csuf454"                       # The database name you've set
DB_USER="csuf454"                       # Your Cloud SQL database user from the screenshot

# Construct the full connection name (for reference, not directly used in connect command below)
# CONNECTION_NAME="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"

# --- Step 1: Connect to the database instance first ---
# This command will prompt you for your DB_USER's password.
# It connects to the instance, but doesn't select a specific database yet.
echo "Attempting to connect to Cloud SQL instance: ${INSTANCE_NAME}"
echo "You will be prompted for the database user's password."

# Use --quiet and --batch for non-interactive mode only if you are passing --execute
# For interactive, just use gcloud sql connect
gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}"

echo "If connection is successful, you will be in the database client prompt (e.g., mysql> or postgres=#)."
echo "Once connected, you MUST manually select the database by typing: USE ${DB_NAME};"
echo "Then you can run your SQL queries."

# --- Example SQL commands to run AFTER connecting and after typing 'USE csuf454;' ---

# To select your database after connecting:
# USE csuf454;

# To show all tables in your 'csuf454' database:
# SHOW TABLES;

# To see the schema (structure) of the 'users' table:
# DESCRIBE users;  # For MySQL
# \d users;      # For PostgreSQL

# To see the schema (structure) of the 'files' table:
# DESCRIBE files;  # For MySQL
# \d files;      # For PostgreSQL

# Select all users:
# SELECT * FROM users;

# Select all files:
# SELECT * FROM files;

# --- To exit the database client, type: ---
# exit;

# --- Step 2: (Optional) Running a single SQL query directly from bash (corrected) ---
# This still requires the password prompt.
# We'll use the --execute flag directly on the gcloud sql connect command,
# and prepend the "USE database_name;" command to the SQL query.
echo -e "\n--- Running a single SQL query (e.g., SELECT VERSION() from ${DB_NAME}) ---"
echo "You will be prompted for the database user's password again."
gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --quiet --batch --execute="USE ${DB_NAME}; SELECT VERSION();"

# Example: Get all users from csuf454 database
# echo -e "\n--- Getting all users from ${DB_NAME} ---"
# gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --quiet --batch --execute="USE ${DB_NAME}; SELECT id, email FROM users;"

# Example: Get all files from csuf454 database
# echo -e "\n--- Getting all files from ${DB_NAME} ---"
# gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}" --quiet --batch --execute="USE ${DB_NAME}; SELECT id, user_id, file_name, cipher_type, save_type FROM files;"
