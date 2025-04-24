import os
import logging
from app.core.app_factory import create_app

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application
application = create_app()

# Get port from environment variable (for Render)
port = int(os.getenv('PORT', 5000))
logger.info(f"Application will listen on port {port}")

if __name__ == "__main__":
    # Run the application with the correct port
    logger.info(f"Starting application on port {port}")
    application.run(host='0.0.0.0', port=port)
