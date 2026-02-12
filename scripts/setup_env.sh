#!/bin/bash
#
# This script sets up the local environment for CyberSentinel.
# It creates a .env file and generates a new secret key.
#

# Check if .env file already exists
if [ -f .env ]; then
  echo ".env file already exists. Skipping creation."
else
  # Check if .env.example exists
  if [ ! -f .env.example ]; then
    echo "ERROR: .env.example not found. Cannot create .env file."
    exit 1
  fi
  echo "--- Creating .env file from .env.example ---"
  cp .env.example .env
fi

# Generate a new secret key and replace the placeholder
echo "--- Generating a new secret key ---"
# This command works on most Linux systems
SECRET_KEY=$(openssl rand -hex 32)

# The sed command differs between macOS and Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
else
  # Linux
  sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
fi

echo "--- .env file is set up ---"
echo "SECRET_KEY has been updated."
echo "Please review the .env file to ensure all other settings are correct."
