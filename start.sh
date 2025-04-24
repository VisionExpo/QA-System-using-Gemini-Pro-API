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
        echo "GOOGLE_API_KEY=AIzaSyCOZ3qbIUsL6a-OyUD-lm13QUgXGFydPSM" > .env
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

# Set environment variables to optimize memory usage
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE=1
export PYTHONHASHSEED=random

# Disable unnecessary services
export DISABLE_VECTOR_DB=true
export DISABLE_SENTENCE_TRANSFORMER=true
export DISABLE_LANGSMITH=true
export LIGHTWEIGHT_MODE=true
export LAZY_LOAD_MODELS=true

# Start gunicorn with extreme memory optimization settings
echo "Starting gunicorn with extreme memory optimization on port $PORT..."
# --timeout 300: Increase worker timeout to 5 minutes
# --workers 1: Use only 1 worker to reduce memory usage
# --threads 1: Use 1 thread per worker to reduce memory usage
# --max-requests 100: Restart workers after 100 requests to prevent memory leaks
# --max-requests-jitter 50: Add jitter to prevent all workers from restarting at once
# --bind: Explicitly bind to the PORT environment variable
# --worker-class=sync: Use sync worker class (simplest, lowest memory usage)
# --worker-tmp-dir /dev/shm: Use shared memory for temporary files
exec gunicorn wsgi:application \
    --timeout 300 \
    --workers 1 \
    --threads 1 \
    --max-requests 100 \
    --max-requests-jitter 50 \
    --worker-class=sync \
    --worker-tmp-dir /dev/shm \
    --bind 0.0.0.0:$PORT \
    "$@"
