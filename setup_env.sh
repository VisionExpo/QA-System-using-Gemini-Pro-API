#!/bin/bash

echo "Setting up virtual environment for QA System using Gemini Pro API..."

# Create virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example. Please edit it to add your API key."
else
    echo ".env file already exists. Make sure it contains your API key."
fi

echo
echo "Setup completed successfully!"
echo
echo "To run the application:"
echo "1. Make sure your virtual environment is activated (you should see (venv) at the beginning of your command prompt)"
echo "2. Run: streamlit run app.py"
echo
echo "To deactivate the virtual environment when done, run: deactivate"
echo
