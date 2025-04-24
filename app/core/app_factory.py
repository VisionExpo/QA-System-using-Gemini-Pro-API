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

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Print environment variables for debugging (excluding sensitive values)
    logger.info("Environment variables loaded. Available keys: %s",
               [k for k in os.environ.keys() if k.startswith(('GOOGLE_', 'ASTRA_', 'FLASK_', 'PYTHON'))])

    # Configure Gemini API
    api_key = os.getenv("GOOGLE_API_KEY")

    # Try alternative methods to get the API key
    if not api_key:
        logger.warning("GOOGLE_API_KEY not found in environment variables. Trying alternative methods...")

        # Try reading from potential config files
        for path in ['/etc/secrets/google_api_key', '/tmp/secrets/google_api_key']:
            try:
                with open(path, 'r') as f:
                    api_key = f.read().strip()
                    logger.info(f"Loaded API key from {path}")
                    break
            except (FileNotFoundError, Exception) as e:
                logger.warning(f"Could not load API key from {path}: {str(e)}")

    if not api_key:
        # List all environment variables for debugging (excluding values)
        env_vars = list(os.environ.keys())
        logger.error(f"Available environment variables: {env_vars}")

        # Check if we're in development or production
        if os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID'):
            # We're on Render - use a hardcoded key for now as a last resort
            logger.warning("Using hardcoded API key as a fallback. Please set GOOGLE_API_KEY in Render dashboard!")
            # Use the key from your .env file
            api_key = 'AIzaSyCp6kib0jZIIbm0DbZfmrbd906AliTVUD4'  # Your API key from .env
        else:
            # In development, we should fail if the key is missing
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
