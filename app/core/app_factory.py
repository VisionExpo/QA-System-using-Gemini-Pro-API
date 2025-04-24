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

    # Try to optimize memory usage
    import gc
    gc.collect()  # Force garbage collection

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Check if we're running on Render
    is_render = bool(os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID'))

    # Print environment variables for debugging (excluding sensitive values)
    logger.info("Environment variables loaded. Available keys: %s",
               [k for k in os.environ.keys() if k.startswith(('GOOGLE_', 'ASTRA_', 'FLASK_', 'PYTHON', 'PORT', 'RENDER'))])

    # Get PORT from environment (for Render)
    port = os.getenv('PORT')
    if port:
        logger.info(f"PORT environment variable found: {port}")
    else:
        logger.warning("PORT environment variable not found, will use default")

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
        if is_render:
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

    # Set configuration for Render deployment
    if is_render:
        # Disable heavy components in production to reduce memory usage
        app.config['DISABLE_VECTOR_DB'] = True
        app.config['DISABLE_SENTENCE_TRANSFORMER'] = True
        app.config['LIGHTWEIGHT_MODE'] = True
        logger.warning("Running in lightweight mode - some features disabled to reduce memory usage")

    # Add a simple health check route that doesn't require any models
    @app.route('/health')
    def health_check():
        return {"status": "ok", "message": "Service is running"}

    # Add a simple root route that doesn't require any models
    @app.route('/')
    def root():
        return """
        <html>
            <head><title>QA System</title></head>
            <body>
                <h1>QA System using Gemini Pro API</h1>
                <p>The service is running. Access the full interface at /chat</p>
                <p><a href="/chat">Go to Chat Interface</a></p>
            </body>
        </html>
        """

    # Register blueprints
    from app.core.routes import main_bp
    app.register_blueprint(main_bp)

    return app
