"""
Enhanced Flask Web App for QA System using Gemini Pro API with ChatGPT-like interface
Supports conversion of PDF, DOCX, audio, and video files to text for processing
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
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
import logging
from werkzeug.utils import secure_filename
from file_processor import process_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Enable CORS
try:
    CORS(app)  # Enable CORS for all routes
    logger.info("CORS enabled for all routes")
except ImportError:
    logger.warning("Warning: flask_cors not installed. CORS is not enabled.")

# Create uploads directory
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create directories for templates and static files
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'},
    'document': {'pdf', 'docx', 'doc'},
    'audio': {'mp3', 'wav', 'ogg', 'flac'},
    'video': {'mp4', 'avi', 'mov', 'mkv'}
}

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in set().union(*ALLOWED_EXTENSIONS.values())

def handle_uploaded_file(file):
    """Process uploaded file and save it to disk"""
    if not file or not allowed_file(file.filename):
        return None, "Invalid file or file type not allowed"
    
    # Create a unique filename
    original_filename = secure_filename(file.filename)
    file_extension = os.path.splitext(original_filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Save the file
    file.save(file_path)
    logger.info(f"Saved uploaded file to {file_path}")
    
    return file_path, None

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
        
        # Get message from request - handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '')
            logger.info(f"Received JSON request with message: {message[:50]}...")
        else:
            message = request.form.get('message', '')
            logger.info(f"Received form request with message: {message[:50]}...")
        
        # Check if there's a file in the request
        file_path = None
        file_info = None
        
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            logger.info(f"Received file: {file.filename}")
            
            # Save and process the file
            file_path, error = handle_uploaded_file(file)
            if error:
                return jsonify({'error': error}), 400
            
            # Process the file to extract text and generate vector representation
            file_info = process_file(file_path)
            logger.info(f"File type: {file_info['file_type']}")
            
            if file_info['error']:
                return jsonify({'error': f"Failed to process the file: {file_info['error']}"}), 400
        
        # Generate content based on message and file
        if file_info and file_info['file_type'] == 'image':
            # For images, use the vision model
            image = Image.open(file_path)
            logger.info(f"Using vision model: {vision_model._model_name}")
            
            if message:
                logger.info(f"Generating content with message and image")
                response = vision_model.generate_content([message, image])
            else:
                logger.info(f"Generating content with image only")
                response = vision_model.generate_content(image)
                
            response_data['answer'] = response.text
        elif file_info and file_info['text']:
            # For text-based files, include the extracted content in the prompt
            file_type = file_info['file_type'].upper()
            extracted_text = file_info['text']
            
            # Create a prompt that includes the file content
            combined_prompt = f"{message}\n\nContent extracted from {file_type} file:\n{extracted_text}"
            logger.info(f"Using text model with extracted content from {file_type}")
            
            response = text_model.generate_content(combined_prompt)
            response_data['answer'] = response.text
        else:
            # Text-only query
            if not message.strip():
                return jsonify({'error': 'No message provided'}), 400
                
            logger.info(f"Using text model for message: {message[:50]}...")
            response = text_model.generate_content(message)
            response_data['answer'] = response.text
        
        # Clean up temporary file if needed
        if file_path and os.path.exists(file_path):
            # Keep files for now for debugging purposes
            # In production, you might want to delete them or implement a cleanup job
            pass
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error in chat route: {str(e)}")
        logger.error(error_traceback)
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

if __name__ == '__main__':
    logger.info("Starting Enhanced Flask app for QA System using Gemini API...")
    logger.info("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
