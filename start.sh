#!/usr/bin/env bash
# This script runs before gunicorn to ensure environment variables are properly set

# Print debug information
echo "Starting application..."
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Running on Render: ${RENDER:-false}"

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
        set -a
        source .env
        set +a

        if [ -n "$GOOGLE_API_KEY" ]; then
            echo "GOOGLE_API_KEY loaded from .env file"
            mkdir -p /tmp/secrets
            echo "$GOOGLE_API_KEY" > /tmp/secrets/google_api_key
        else
            echo "ERROR: GOOGLE_API_KEY not found in .env file"
        fi
    else
        echo "ERROR: No .env file found"

        # Create a .env file with hardcoded values as a last resort
        echo "Creating .env file with hardcoded values as a last resort..."
        echo "GOOGLE_API_KEY=AIzaSyCp6kib0jZIIbm0DbZfmrbd906AliTVUD4" > .env
        echo "Created .env file with hardcoded API key"

        # Load the newly created .env file
        set -a
        source .env
        set +a

        # Save to a temporary file that our app can read
        mkdir -p /tmp/secrets
        echo "$GOOGLE_API_KEY" > /tmp/secrets/google_api_key
    fi
fi

# List all environment variables for debugging
echo "All environment variables (names only):"
printenv | cut -d= -f1 | sort

# List specific environment variables (names only, not values)
echo "Specific environment variables:"
printenv | grep -E "GOOGLE_|ASTRA_|FLASK_|PYTHON|RENDER" | cut -d= -f1

# Get the PORT from environment variable (for Render)
PORT=${PORT:-5000}
echo "PORT environment variable: $PORT"

# Start gunicorn with optimized settings for memory usage
echo "Starting gunicorn with optimized settings on port $PORT..."
# --timeout 180: Increase worker timeout to 180 seconds (3 minutes)
# --workers 1: Use only 1 worker to reduce memory usage
# --threads 2: Use 2 threads per worker for concurrency
# --max-requests 1000: Restart workers after 1000 requests to prevent memory leaks
# --max-requests-jitter 50: Add jitter to prevent all workers from restarting at once
# --preload: Load application code before forking worker processes
# --bind: Explicitly bind to the PORT environment variable
exec gunicorn wsgi:application \
    --timeout 180 \
    --workers 1 \
    --threads 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --bind 0.0.0.0:$PORT \
    "$@"
