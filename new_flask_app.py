"""
Flask Web App for QA System using Gemini Pro API with ChatGPT-like interface
"""

from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import io
import base64
import uuid
import tempfile
import mimetypes
import re
import json
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# Initialize models
text_model = genai.GenerativeModel('gemini-1.5-pro')
vision_model = genai.GenerativeModel('gemini-1.5-flash')  # Using the recommended model

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create directories for templates and static files
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# File processing functions
def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        # This is a placeholder - in a real app, you would use PyMuPDF (fitz)
        # or another PDF library to extract text
        return f"[PDF text extraction from {file_path}]"
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        # This is a placeholder - in a real app, you would use docx2txt
        # or another DOCX library to extract text
        return f"[DOCX text extraction from {file_path}]"
    except Exception as e:
        print(f"Error extracting text from DOCX: {str(e)}")
        return ""

def transcribe_audio(file_path):
    """Transcribe audio file to text"""
    try:
        # This is a placeholder - in a real app, you would use SpeechRecognition
        # or another audio transcription library
        return f"[Audio transcription from {file_path}]"
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return ""

def process_file(file):
    """Process uploaded file based on its type"""
    if not file:
        return None, None
        
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    mime_type = mimetypes.guess_type(file_path)[0]
    file_type = None
    extracted_content = None
    
    if mime_type:
        if mime_type.startswith('image/'):
            file_type = 'image'
            # We'll process the image directly in the chat route
            extracted_content = file_path
        elif mime_type == 'application/pdf':
            file_type = 'pdf'
            extracted_content = extract_text_from_pdf(file_path)
        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            file_type = 'docx'
            extracted_content = extract_text_from_docx(file_path)
        elif mime_type.startswith('audio/'):
            file_type = 'audio'
            extracted_content = transcribe_audio(file_path)
        else:
            file_type = 'unknown'
            extracted_content = f"Unsupported file type: {mime_type}"
    
    return file_type, extracted_content

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Initialize response
        response_data = {
            'answer': '',
            'error': None
        }
        
        # Get message from request
        message = request.form.get('message', '')
        
        # Check if there's a file in the request
        file_type = None
        file_content = None
        
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            print(f"Received file: {file.filename}")
            
            # Process the file based on its type
            file_type, file_content = process_file(file)
            print(f"File type: {file_type}")
            
            if not file_type or not file_content:
                return jsonify({'error': 'Failed to process the file'}), 400
        
        # Generate content based on message and file
        if file_type == 'image':
            # For images, use the vision model
            image = Image.open(file_content)
            print(f"Using vision model: {vision_model._model_name}")
            
            if message:
                print(f"Generating content with message and image")
                response = vision_model.generate_content([message, image])
            else:
                print(f"Generating content with image only")
                response = vision_model.generate_content(image)
                
            response_data['answer'] = response.text
        elif file_type in ['pdf', 'docx', 'audio']:
            # For text-based files, include the extracted content in the prompt
            combined_prompt = f"{message}\n\nContent extracted from {file_type.upper()} file:\n{file_content}"
            print(f"Using text model with extracted content from {file_type}")
            response = text_model.generate_content(combined_prompt)
            response_data['answer'] = response.text
        else:
            # Text-only query
            if not message.strip():
                return jsonify({'error': 'No message provided'}), 400
                
            print(f"Using text model for message: {message[:50]}...")
            response = text_model.generate_content(message)
            response_data['answer'] = response.text
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in chat route: {str(e)}")
        print(error_traceback)
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

if __name__ == '__main__':
    print("Starting Flask app for QA System using Gemini API...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
