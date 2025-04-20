"""
Enhanced Flask Web App for QA System using Gemini Pro API with ChatGPT-like interface
Supports YouTube video processing and AstraDB vector database integration
"""

import os
import logging
from dotenv import load_dotenv
from app.core.app_factory import create_app

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set LangSmith environment variables if not already set
if not os.getenv("LANGCHAIN_API_KEY"):
    logger.warning("LANGCHAIN_API_KEY not set. LangSmith monitoring will be disabled.")
    logger.warning("Get your API key from https://smith.langchain.com and add it to your .env file")

# Set LangSmith tracing to True by default
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "qa-system-gemini")

# Create Flask app
app = create_app()

if __name__ == '__main__':
    logger.info("Starting Enhanced QA System with Gemini API...")
    logger.info("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True)
