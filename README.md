# QA System using Gemini Pro API

A Question and Answer system built with Google's Gemini Pro API.

## Application Features

This project provides a Q&A interface using Google's Gemini models:

- Text-based Q&A using Gemini Pro (app.py)
- Image analysis using Gemini Pro Vision (vision.py)
- Deployment: [https://qa-system-using-gemini-pro-api-1.onrender.com/](https://qa-system-using-gemini-pro-api-1.onrender.com/)

## Key Features

- **Text Q&A**: Ask questions and get detailed answers
- **Image Analysis**: Upload images for AI-powered analysis
- **User-friendly Interface**: Clean Streamlit interface
- **API Integration**: Seamless integration with Google's Gemini API
- **Environment Variable Support**: Secure API key management

## Project Structure

```plaintext
.
├── Gemini LLM App/         # Main application directory
│   ├── app.py              # Text Q&A application
│   ├── vision.py           # Image analysis application
│   └── requirements.txt    # Dependencies
├── app.py                  # Enhanced Q&A application
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
├── .env.example            # Example environment variables file
├── .gitignore              # Git ignore file
├── setup_env.bat           # Windows setup script
├── setup_env.sh            # macOS/Linux setup script
└── venv/                   # Virtual environment (not tracked by git)
```

## Development Setup

### Virtual Environment

This project uses a virtual environment to isolate dependencies. The `.gitignore` file is configured to exclude the virtual environment directory from version control.

### .gitignore

The `.gitignore` file is set up to exclude:

- Virtual environment directories (`venv/`, `.venv/`, etc.)
- Python cache files and bytecode
- Environment variables file (`.env`)
- Log files
- IDE-specific files
- Build artifacts

## Installation

### Option 1: Using Setup Scripts (Recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/QA-System-using-Gemini-Pro-API.git
   cd QA-System-using-Gemini-Pro-API
   ```

2. Run the setup script:

   **For Windows:**

   ```bash
   setup_env.bat
   ```

   **For macOS/Linux:**

   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

   This script will:
   - Create a virtual environment
   - Activate the virtual environment
   - Install dependencies
   - Create a `.env` file from the example if it doesn't exist

3. Edit the `.env` file and replace `your_api_key_here` with your actual API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### Option 2: Manual Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/QA-System-using-Gemini-Pro-API.git
   cd QA-System-using-Gemini-Pro-API
   ```

2. Create and activate a virtual environment:

   **For Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **For macOS/Linux:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   You should see `(venv)` at the beginning of your command prompt, indicating that the virtual environment is active.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:

   Copy the example environment file and add your Google API key:

   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file and replace `your_api_key_here` with your actual API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Usage

### Running the Application

```bash
streamlit run app.py
```

### Deactivating the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:

```bash
deactivate
```

### Text Q&A Mode

In this mode, you can ask text-based questions and receive detailed answers from the Gemini Pro model.

### Image Analysis Mode

In this mode, you can upload images and optionally provide a prompt to get AI-powered analysis of the image content.

### Example Usage

```python
# Import required libraries
from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize model
model = genai.GenerativeModel('gemini-pro')

# Get response
def get_response(question):
    response = model.generate_content(question)
    return response.text
```
