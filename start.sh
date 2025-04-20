#!/usr/bin/env bash
# This script runs before gunicorn to ensure environment variables are properly set

# Print debug information
echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"

# Check for environment variables
echo "Checking environment variables..."
if [ -n "$GOOGLE_API_KEY" ]; then
    echo "GOOGLE_API_KEY is set"
    # Save to a temporary file that our app can read
    mkdir -p /tmp/secrets
    echo "$GOOGLE_API_KEY" > /tmp/secrets/google_api_key
    echo "Saved API key to /tmp/secrets/google_api_key"
else
    echo "WARNING: GOOGLE_API_KEY is not set in the environment"
    # Check if we have a .env file
    if [ -f .env ]; then
        echo "Found .env file, loading variables..."
        export $(grep -v '^#' .env | xargs)
        if [ -n "$GOOGLE_API_KEY" ]; then
            echo "GOOGLE_API_KEY loaded from .env file"
            mkdir -p /tmp/secrets
            echo "$GOOGLE_API_KEY" > /tmp/secrets/google_api_key
        else
            echo "ERROR: GOOGLE_API_KEY not found in .env file"
        fi
    else
        echo "ERROR: No .env file found"
    fi
fi

# List available environment variables (names only, not values)
echo "Available environment variables:"
printenv | grep -E "GOOGLE_|ASTRA_|FLASK_|PYTHON" | cut -d= -f1

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn wsgi:application "$@"
