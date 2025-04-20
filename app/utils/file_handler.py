"""
File handling utilities for the QA System
"""

import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app

# Set up logging
logger = logging.getLogger(__name__)

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
    
    # Get the upload folder from app config
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(file_path)
    logger.info(f"Saved uploaded file to {file_path}")
    
    return file_path, None
