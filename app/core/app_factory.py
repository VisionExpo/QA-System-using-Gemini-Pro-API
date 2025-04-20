"""
Flask app factory for QA System
"""

import os
import logging
import google.generativeai as genai
from flask import Flask
from flask_cors import CORS

# Set up logging
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app"""
    
    # Configure Gemini API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.secret_key = os.getenv("SECRET_KEY", os.urandom(24).hex())
    
    # Enable CORS
    try:
        CORS(app)  # Enable CORS for all routes
        logger.info("CORS enabled for all routes")
    except ImportError:
        logger.warning("Warning: flask_cors not installed. CORS is not enabled.")
    
    # Create uploads directory
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    # Register blueprints
    from app.core.routes import main_bp
    app.register_blueprint(main_bp)
    
    return app
