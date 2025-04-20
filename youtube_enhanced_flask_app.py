"""
Enhanced Flask Web App for QA System using Gemini Pro API with ChatGPT-like interface
Supports YouTube video processing and AstraDB vector database integration
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
from file_processor import process_file, is_url, is_youtube_url
from astra_db import get_astra_db_manager

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

# Initialize AstraDB manager
astra_db_manager = get_astra_db_manager()
if astra_db_manager.is_connected:
    logger.info("Successfully connected to AstraDB")
else:
    logger.warning("Not connected to AstraDB. Vector database functionality will be limited.")

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

def store_in_vector_db(text, vector, metadata=None):
    """Store text and vector in AstraDB"""
    if not astra_db_manager.is_connected:
        logger.warning("AstraDB not connected. Cannot store vector.")
        return None
    
    try:
        # Add timestamp to metadata
        if not metadata:
            metadata = {}
        
        # Store in AstraDB
        doc_id = astra_db_manager.store_vector(text, vector, metadata)
        if doc_id:
            logger.info(f"Stored vector in AstraDB with ID: {doc_id}")
        return doc_id
    except Exception as e:
        logger.error(f"Error storing vector in AstraDB: {str(e)}")
        return None

def find_similar_content(vector, limit=3):
    """Find similar content in AstraDB"""
    if not astra_db_manager.is_connected:
        logger.warning("AstraDB not connected. Cannot search for similar content.")
        return []
    
    try:
        # Search for similar vectors
        results = astra_db_manager.search_similar(vector, limit=limit)
        if results:
            logger.info(f"Found {len(results)} similar documents in AstraDB")
        return results
    except Exception as e:
        logger.error(f"Error searching for similar content in AstraDB: {str(e)}")
        return []

def summarize_youtube_video(url, transcript):
    """Generate a summary of a YouTube video using Gemini"""
    try:
        # Create a prompt for summarization
        prompt = f"""
        Please provide a comprehensive summary of the following YouTube video transcript.
        Focus on the main points, key insights, and important details.
        
        Video URL: {url}
        
        Transcript:
        {transcript[:10000]}  # Limit transcript length to avoid token limits
        
        Please structure your summary with:
        1. A brief overview (1-2 sentences)
        2. Main topics covered
        3. Key points and insights
        4. Conclusion or takeaways
        """
        
        # Generate summary
        response = text_model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        logger.error(f"Error summarizing YouTube video: {str(e)}")
        return f"Error generating summary: {str(e)}"

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
            'error': None,
            'similar_content': []
        }
        
        # Get message from request - handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '')
            logger.info(f"Received JSON request with message: {message[:50]}...")
        else:
            message = request.form.get('message', '')
            logger.info(f"Received form request with message: {message[:50]}...")
        
        # Check if the message is a URL
        is_message_url = is_url(message)
        file_info = None
        
        # Process URL in message if it's a URL
        if is_message_url:
            logger.info(f"Message contains URL: {message}")
            file_info = process_file(message)
            
            # If it's a YouTube URL, we'll handle it specially
            if file_info and file_info['file_type'] == 'youtube':
                logger.info(f"Processing YouTube URL: {message}")
                
                # Check if we have a transcript
                if file_info['text'] and not file_info['error']:
                    # Generate a summary
                    summary = summarize_youtube_video(message, file_info['text'])
                    
                    # Store in vector database if available
                    if file_info['vector'] is not None and astra_db_manager.is_connected:
                        metadata = {
                            'type': 'youtube',
                            'url': message,
                            'summary': summary[:500]  # Store a snippet of the summary
                        }
                        doc_id = store_in_vector_db(file_info['text'], file_info['vector'], metadata)
                        if doc_id:
                            logger.info(f"Stored YouTube transcript in AstraDB with ID: {doc_id}")
                    
                    # Set the response
                    response_data['answer'] = summary
                    return jsonify(response_data)
        
        # Check if there's a file in the request
        file_path = None
        
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
        
        # Find similar content if we have a vector
        similar_content = []
        if file_info and file_info['vector'] is not None and astra_db_manager.is_connected:
            similar_docs = find_similar_content(file_info['vector'])
            for doc in similar_docs:
                if '_id' in doc and 'text' in doc:
                    # Only include a snippet of the text to avoid large responses
                    text_snippet = doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text']
                    similar_content.append({
                        'id': doc['_id'],
                        'text': text_snippet,
                        'type': doc.get('type', 'unknown'),
                        'url': doc.get('url', None),
                        'similarity': doc.get('$similarity', 0)
                    })
            
            response_data['similar_content'] = similar_content
        
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
            
            # Store in vector database if available
            if file_info['vector'] is not None and astra_db_manager.is_connected:
                metadata = {
                    'type': file_info['file_type'],
                    'query': message,
                    'answer': response_data['answer'][:500]  # Store a snippet of the answer
                }
                doc_id = store_in_vector_db(extracted_text, file_info['vector'], metadata)
                if doc_id:
                    logger.info(f"Stored {file_type} content in AstraDB with ID: {doc_id}")
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
    logger.info("Starting YouTube-Enhanced Flask app for QA System using Gemini API...")
    logger.info("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
