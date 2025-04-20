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
└── requirements.txt        # Dependencies
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/QA-System-using-Gemini-Pro-API.git
   cd QA-System-using-Gemini-Pro-API
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:

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
