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

    # Configure Gemini API - but don't initialize the model yet
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
            api_key = 'AIzaSyCOZ3qbIUsL6a-OyUD-lm13QUgXGFydPSM'  # Your API key from .env
        else:
            # In development, we should fail if the key is missing
            raise ValueError("GOOGLE_API_KEY environment variable not set")

    # Configure Gemini API but don't initialize models yet
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
        app.config['DISABLE_LANGSMITH'] = True
        app.config['LIGHTWEIGHT_MODE'] = True
        app.config['LAZY_LOAD_MODELS'] = True
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

    # Create a minimal chat route that doesn't require loading the full blueprint
    @app.route('/chat')
    def minimal_chat():
        return """
        <html>
            <head>
                <title>QA System - Chat</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                    .chat-container { max-width: 800px; margin: 0 auto; }
                    .message { padding: 10px; margin-bottom: 10px; border-radius: 5px; }
                    .user { background-color: #e6f7ff; text-align: right; }
                    .bot { background-color: #f0f0f0; }
                    textarea { width: 100%; padding: 10px; margin-top: 20px; }
                    button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="chat-container">
                    <h1>QA System using Gemini Pro API</h1>
                    <p>This is a minimal chat interface. The full functionality is disabled in lightweight mode.</p>
                    <div class="message bot">Hello! I'm running in lightweight mode to conserve memory. Ask me a simple question!</div>
                    <div id="messages"></div>
                    <textarea id="user-input" placeholder="Type your message here..."></textarea>
                    <button onclick="sendMessage()">Send</button>
                </div>
                <script>
                    function sendMessage() {
                        const input = document.getElementById('user-input');
                        const message = input.value.trim();
                        if (message) {
                            // Add user message
                            const messagesDiv = document.getElementById('messages');
                            messagesDiv.innerHTML += `<div class="message user">${message}</div>`;

                            // Add bot response
                            messagesDiv.innerHTML += `<div class="message bot">I'm running in lightweight mode. Full functionality is disabled to conserve memory on Render.</div>`;

                            // Clear input
                            input.value = '';
                        }
                    }
                </script>
            </body>
        </html>
        """

    # Only register blueprints if not in lightweight mode
    if not is_render:
        try:
            from app.core.routes import main_bp
            app.register_blueprint(main_bp)
        except Exception as e:
            logger.error(f"Error registering blueprints: {str(e)}")
            # Continue without blueprints in lightweight mode

    return app
