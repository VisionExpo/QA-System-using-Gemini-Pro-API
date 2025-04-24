import os
import logging
import gc

# Force garbage collection to free up memory
gc.collect()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if we're running on Render
is_render = bool(os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID'))

# Get port from environment variable (for Render)
port = int(os.getenv('PORT', 5000))
logger.info(f"Application will listen on port {port}")

# Create the Flask application - import only when needed
from app.core.app_factory import create_app
application = create_app()

# Force garbage collection again after app creation
gc.collect()

if __name__ == "__main__":
    # Run the application with the correct port
    logger.info(f"Starting application on port {port}")
    application.run(host='0.0.0.0', port=port)
