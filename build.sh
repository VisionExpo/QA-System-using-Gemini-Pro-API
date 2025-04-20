#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p temp

# Print versions for debugging
python --version
pip --version
echo "Build completed successfully!"
