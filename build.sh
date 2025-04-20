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

# Print versions and environment for debugging
python --version
pip --version
python -c "import sys; print(sys.path)"
echo "Build completed successfully!"
