#!/bin/bash

# --- Configuration Variables ---
# IMPORTANT: Replace these with your actual Cloud SQL instance details
PROJECT_ID="forward-scion-465216-s9"     # Your Google Cloud Project ID from the screenshot
REGION="us-west1"                       # Your instance region from the screenshot
INSTANCE_NAME="csuf454"             # *** IMPORTANT: REPLACE WITH YOUR EXACT CLOUD SQL INSTANCE ID ***
DB_NAME="csuf454"                       # The database name you've set
DB_USER="csuf454"                       # Your Cloud SQL database user

# --- Step 1: Connect to the database instance interactively ---
# This command will prompt you for your DB_USER's password.
echo "Attempting to connect to Cloud SQL instance: ${INSTANCE_NAME}"
echo "You will be prompted for the database user's password."

# Connect to the instance. You will then manually select the database.
gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}"

echo "If connection is successful, you will be in the database client prompt (e.g., mysql> or postgres=#)."
echo "Once connected, you MUST manually select the database by typing: USE ${DB_NAME};"
echo "Then you can run your SQL queries."

# --- To exit the database client, type: ---
# exit;

# --- Step 2: (Optional) Running a single SQL query directly from bash (CORRECTED) ---
# This uses 'gcloud sql databases query' which is designed for non-interactive queries.
echo -e "\n--- Running a single SQL query (e.g., SELECT VERSION() from ${DB_NAME}) ---"
echo "You will be prompted for the database user's password again."

gcloud sql databases query "${DB_NAME}" \
  --instance="${INSTANCE_NAME}" \
  --database="${DB_NAME}" \
  --user="${DB_USER}" \
  --query="SELECT VERSION();" \
  --format="json" # Or "table", "csv" for different output formats

# Example: Get all users from csuf454 database (non-interactive)
# echo -e "\n--- Getting all users from ${DB_NAME} (non-interactive) ---"
# gcloud sql databases query "${DB_NAME}" \
#   --instance="${INSTANCE_NAME}" \
#   --database="${DB_NAME}" \
#   --user="${DB_USER}" \
#   --query="SELECT id, email FROM users;" \
#   --format="table"

# Example: Get all files from csuf454 database (non-interactive)
# echo -e "\n--- Getting all files from ${DB_NAME} (non-interactive) ---"
# gcloud sql databases query "${DB_NAME}" \
#   --instance="${INSTANCE_NAME}" \
#   --database="${DB_NAME}" \
#   --user="${DB_USER}" \
#   --query="SELECT id, user_id, file_name, cipher_type, save_type FROM files;" \
#   --format="table"
