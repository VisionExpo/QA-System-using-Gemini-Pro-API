# Utility Scripts

This folder contains utility scripts for testing and debugging the Gemini API integration.

## Available Scripts

### ask_question.py

A simple command-line interface to ask questions to the Gemini Pro API.

**Usage:**
```bash
python scripts/ask_question.py
```

This will start an interactive session where you can ask questions to the Gemini Pro API.

### list_models.py

A script to list all available models in Google Generative AI.

**Usage:**
```bash
python scripts/list_models.py
```

This will print a list of all available models and their supported generation methods.

## Requirements

These scripts require the same environment variables as the main application:

- `GOOGLE_API_KEY`: Your Google API key for accessing the Gemini API

Make sure your `.env` file is properly configured before running these scripts.
