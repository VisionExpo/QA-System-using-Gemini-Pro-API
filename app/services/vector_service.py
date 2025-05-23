"""
Vector database service for the QA System
"""

import logging

# Set up logging
logger = logging.getLogger(__name__)

# Check if we're in lightweight mode (for Render deployment)
from flask import current_app
lightweight_mode = False

# Function to check if vector DB is disabled
def is_vector_db_disabled():
    """Check if vector DB is disabled in the current app config"""
    try:
        if current_app and current_app.config.get('DISABLE_VECTOR_DB'):
            logger.warning("Vector database disabled in lightweight mode")
            return True
        return False
    except RuntimeError:  # Outside of application context
        return lightweight_mode

# Try to import AstraDB manager, but continue if it fails
try:
    # Check if we're in lightweight mode
    if is_vector_db_disabled():
        astra_available = False
        logger.warning("Vector database functionality disabled in lightweight mode")
    else:
        from app.services.astra_db import get_astra_db_manager
        astra_db_manager = get_astra_db_manager()
        astra_available = astra_db_manager.is_connected
        if astra_available:
            logger.info("Successfully connected to AstraDB")
        else:
            logger.warning("Not connected to AstraDB. Vector database functionality will be limited.")
except ImportError:
    astra_available = False
    logger.warning("AstraDB module could not be imported. Vector database functionality will be disabled.")
except Exception as e:
    astra_available = False
    logger.error(f"Error initializing AstraDB: {str(e)}")

def store_in_vector_db(text, vector, metadata=None):
    """Store text and vector in AstraDB"""
    # Check if vector DB is disabled in lightweight mode
    if is_vector_db_disabled():
        logger.warning("Vector database disabled in lightweight mode. Cannot store vector.")
        return None

    if not astra_available:
        logger.warning("AstraDB not available. Cannot store vector.")
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
    # Check if vector DB is disabled in lightweight mode
    if is_vector_db_disabled():
        logger.warning("Vector database disabled in lightweight mode. Cannot search for similar content.")
        return []

    if not astra_available:
        logger.warning("AstraDB not available. Cannot search for similar content.")
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

def store_qa_pair(question, answer, vector=None, metadata=None):
    """Store a question-answer pair in AstraDB"""
    # Check if vector DB is disabled in lightweight mode
    if is_vector_db_disabled():
        logger.warning("Vector database disabled in lightweight mode. Cannot store Q&A pair.")
        return None

    if not astra_available:
        logger.warning("AstraDB not available. Cannot store Q&A pair.")
        return None

    # Import here to avoid circular imports
    from app.services.file_processor import text_to_vector

    try:
        # Create combined text
        qa_text = f"Question: {question}\n\nAnswer: {answer}"

        # Add metadata
        if not metadata:
            metadata = {}

        metadata.update({
            "type": "qa_pair",
            "question": question,
            "answer": answer
        })

        # Generate vector if not provided
        if vector is None:
            logger.info("No vector provided for Q&A pair, generating one")
            vector = text_to_vector(qa_text)

        # Double-check that we have a vector
        if vector is None:
            logger.error("Failed to generate vector for Q&A pair")
            return None

        # Store in AstraDB
        doc_id = astra_db_manager.store_vector(qa_text, vector, metadata)
        if doc_id:
            logger.info(f"Stored Q&A pair in AstraDB with ID: {doc_id}")
        else:
            logger.error("Failed to store Q&A pair in AstraDB")
        return doc_id
    except Exception as e:
        logger.error(f"Error storing Q&A pair in AstraDB: {str(e)}")
        return None
