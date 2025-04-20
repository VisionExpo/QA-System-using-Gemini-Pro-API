#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p app/uploads
mkdir -p app/temp
mkdir -p uploads
mkdir -p temp

# Make sure the app is importable
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Create a .env file if it doesn't exist (for development only)
if [ ! -f .env ] && [ -f .env.example ]; then
    echo "Creating .env file from .env.example for development"
    cp .env.example .env
fi

# Debug: Check if environment variables are set
echo "Checking for environment variables..."
if [ -n "$GOOGLE_API_KEY" ]; then
    echo "GOOGLE_API_KEY is set"
else
    echo "WARNING: GOOGLE_API_KEY is not set"
fi

# Create a secrets directory for alternative access methods
mkdir -p /tmp/secrets
if [ -n "$GOOGLE_API_KEY" ]; then
    echo "$GOOGLE_API_KEY" > /tmp/secrets/google_api_key
    echo "Saved API key to /tmp/secrets/google_api_key"
fi

# Print versions and environment for debugging
python --version
pip --version
python -c "import sys; print(sys.path)"
echo "Environment variables available:"
printenv | grep -E "GOOGLE_|ASTRA_|FLASK_|PYTHON" | cut -d= -f1
echo "Build completed successfully!"
