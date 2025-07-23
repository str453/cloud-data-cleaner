#!/bin/bash

# --- Configuration Variables ---
# IMPORTANT: Replace these with your actual Cloud SQL instance details
PROJECT_ID="forward-scion-465216-s9"     # Your Google Cloud Project ID
REGION="us-west1"                       # Your instance region
INSTANCE_NAME="csuf454"                 # Your Cloud SQL Instance ID (from previous step)
DB_NAME="csuf454"                       # The database name you've set
DB_USER="csuf454"                       # Your Cloud SQL database user

# --- Step 1: Connect to the database instance interactively ---
# This command will prompt you for your DB_USER's password.
echo "Attempting to connect to Cloud SQL instance: ${INSTANCE_NAME}"
echo "You will be prompted for the database user's password."

# Connect to the instance.
gcloud sql connect "${INSTANCE_NAME}" --user="${DB_USER}"

echo "If connection is successful, you will be in the database client prompt (e.g., mysql> or postgres=#)."
echo "Follow the steps below within that client to check your schema:"
echo ""
echo "--- SQL Commands to Run in the Database Client ---"
echo "1. Select your database:"
echo "   For MySQL/SQL Server: USE ${DB_NAME};"
echo "   For PostgreSQL:       \\c ${DB_NAME};"
echo ""
echo "2. Show all tables to confirm they exist:"
echo "   For MySQL/SQL Server: SHOW TABLES;"
echo "   For PostgreSQL:       \\dt;"
echo ""
echo "3. Describe the 'users' table (check columns, types, keys):"
echo "   For MySQL/SQL Server: DESCRIBE users;"
echo "   For PostgreSQL:       \\d users;"
echo ""
echo "4. Describe the 'files' table (check columns, types, keys):"
echo "   For MySQL/SQL Server: DESCRIBE files;"
echo "   For PostgreSQL:       \\d files;"
echo ""
echo "--- To exit the database client, type: exit; ---"
