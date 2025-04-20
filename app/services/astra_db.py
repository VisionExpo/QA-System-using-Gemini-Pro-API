"""
AstraDB integration for QA System using Gemini API
Handles vector storage and retrieval
"""

import os
import logging
import json
import uuid
from dotenv import load_dotenv
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Import AstraDB with error handling
try:
    from astrapy.db import AstraDB
    astradb_available = True
    logger.info("AstraDB package successfully imported")
except ImportError:
    astradb_available = False
    logger.warning("AstraDB not installed. Vector database functionality will be unavailable.")

# Load environment variables
load_dotenv()

# AstraDB configuration
ASTRA_DB_TOKEN_FILE = os.getenv("ASTRA_DB_TOKEN_FILE", "gorulevishal984@gmail.com-token.json")
ASTRA_DB_COLLECTION = os.getenv("ASTRA_DB_COLLECTION", "qa_system_vectors")

# Try to load token from file
def load_astra_token():
    try:
        if os.path.exists(ASTRA_DB_TOKEN_FILE):
            with open(ASTRA_DB_TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                logger.info(f"Successfully loaded AstraDB token from {ASTRA_DB_TOKEN_FILE}")

                # Extract token
                token = token_data.get('token')

                # Construct API endpoint from token data
                # Format: https://{DB_ID}-{REGION}.apps.astra.datastax.com
                # For this example, we'll use a default endpoint if not provided
                endpoint = os.getenv("ASTRA_DB_API_ENDPOINT", "https://api.astra.datastax.com/v2/namespaces/default_keyspace/collections")

                return token, endpoint
        else:
            logger.warning(f"AstraDB token file not found: {ASTRA_DB_TOKEN_FILE}")
            # Fall back to environment variables
            return os.getenv("ASTRA_DB_APPLICATION_TOKEN"), os.getenv("ASTRA_DB_API_ENDPOINT")
    except Exception as e:
        logger.error(f"Error loading AstraDB token: {str(e)}")
        return None, None

ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT = load_astra_token()

class AstraDBManager:
    """Manager for AstraDB operations"""

    def __init__(self):
        """Initialize AstraDB connection"""
        self.db = None
        self.collection = None
        self.is_connected = False

        if not astradb_available:
            logger.error("AstraDB not available. Install astrapy package.")
            return

        if not ASTRA_DB_APPLICATION_TOKEN or not ASTRA_DB_API_ENDPOINT:
            logger.error("AstraDB credentials not found in environment variables or token file.")
            return

        try:
            # Log connection attempt
            logger.info(f"Attempting to connect to AstraDB with token: {ASTRA_DB_APPLICATION_TOKEN[:10]}...")
            logger.info(f"API endpoint: {ASTRA_DB_API_ENDPOINT}")

            # Initialize AstraDB
            self.db = AstraDB(
                api_endpoint=ASTRA_DB_API_ENDPOINT,
                token=ASTRA_DB_APPLICATION_TOKEN
            )

            # Create or get collection
            self.collection = self.db.create_collection(
                collection_name=ASTRA_DB_COLLECTION,
                dimension=384  # Dimension of the sentence-transformers embeddings
            )

            self.is_connected = True
            logger.info(f"Successfully connected to AstraDB collection: {ASTRA_DB_COLLECTION}")
        except Exception as e:
            logger.error(f"Error connecting to AstraDB: {str(e)}")

    def store_vector(self, text, vector, metadata=None):
        """Store a vector in AstraDB"""
        if not self.is_connected:
            logger.error("Not connected to AstraDB")
            return None

        try:
            # Prepare document
            document = {
                "_id": str(uuid.uuid4()),
                "text": text,
                "$vector": vector.tolist() if hasattr(vector, 'tolist') else vector,
                "timestamp": datetime.now().isoformat()
            }

            # Add metadata if provided
            if metadata:
                document.update(metadata)

            # Insert document
            result = self.collection.insert_one(document)
            logger.info(f"Successfully stored vector with ID: {result['_id']}")
            return result["_id"]
        except Exception as e:
            logger.error(f"Error storing vector in AstraDB: {str(e)}")
            return None

    def search_similar(self, vector, limit=5):
        """Search for similar vectors in AstraDB"""
        if not self.is_connected:
            logger.error("Not connected to AstraDB")
            return []

        try:
            # Convert numpy array to list if needed
            if hasattr(vector, 'tolist'):
                vector = vector.tolist()

            # Perform similarity search
            results = self.collection.vector_find(
                vector=vector,
                limit=limit
            )

            logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error searching similar vectors in AstraDB: {str(e)}")
            return []

    def delete_document(self, document_id):
        """Delete a document from AstraDB"""
        if not self.is_connected:
            logger.error("Not connected to AstraDB")
            return False

        try:
            result = self.collection.delete_one({"_id": document_id})
            success = result.get("deletedCount", 0) > 0
            if success:
                logger.info(f"Successfully deleted document with ID: {document_id}")
            else:
                logger.warning(f"Document with ID {document_id} not found")
            return success
        except Exception as e:
            logger.error(f"Error deleting document from AstraDB: {str(e)}")
            return False

    def get_document(self, document_id):
        """Get a document from AstraDB by ID"""
        if not self.is_connected:
            logger.error("Not connected to AstraDB")
            return None

        try:
            result = self.collection.find_one({"_id": document_id})
            if result:
                logger.info(f"Successfully retrieved document with ID: {document_id}")
            else:
                logger.warning(f"Document with ID {document_id} not found")
            return result
        except Exception as e:
            logger.error(f"Error getting document from AstraDB: {str(e)}")
            return None

# Create a singleton instance
astra_db_manager = AstraDBManager()

def get_astra_db_manager():
    """Get the AstraDB manager instance"""
    return astra_db_manager
