"""
QA System using Gemini Pro API
"""

import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'temp'), exist_ok=True)

# This allows the app package to be imported directly
__version__ = '1.0.0'
