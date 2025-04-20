"""
List available models in Google Generative AI
"""

from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# List available models
print("Available Models:")
for model in genai.list_models():
    print(f"- {model.name}")
    print(f"  Supported generation methods: {model.supported_generation_methods}")
    print()
