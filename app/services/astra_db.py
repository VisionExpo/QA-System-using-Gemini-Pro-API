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
    from astrapy import DataAPIClient
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

                # Extract token - this should be the full token string
                token = token_data.get('token')
                if not token:
                    # Try alternative key names that might be in the token file
                    token = token_data.get('clientId') or token_data.get('client_id') or token_data.get('astra_token')

                # Get API endpoint
                endpoint = token_data.get('endpoint') or token_data.get('api_endpoint') or token_data.get('astra_api_endpoint')

                # If no endpoint in token file, use environment variable or default
                if not endpoint:
                    endpoint = os.getenv("ASTRA_DB_API_ENDPOINT",
                                        "https://633e05a8-a7b4-461d-ad6e-582f097793b7-us-east-2.apps.astra.datastax.com")

                logger.info(f"Using AstraDB endpoint: {endpoint}")
                return token, endpoint
        else:
            logger.warning(f"AstraDB token file not found: {ASTRA_DB_TOKEN_FILE}")
            # Fall back to environment variables
            token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            endpoint = os.getenv("ASTRA_DB_API_ENDPOINT",
                               "https://633e05a8-a7b4-461d-ad6e-582f097793b7-us-east-2.apps.astra.datastax.com")
            return token, endpoint
    except Exception as e:
        logger.error(f"Error loading AstraDB token: {str(e)}")
        return None, None

ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_API_ENDPOINT = load_astra_token()

class AstraDBManager:
    """Manager for AstraDB operations"""

    def __init__(self):
        """Initialize AstraDB connection"""
        self.client = None
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

            # Initialize AstraDB client
            self.client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)

            # Get the database
            self.db = self.client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)

            # Check if collection exists, create if not
            collection_names = self.db.list_collection_names()
            logger.info(f"Available collections: {collection_names}")

            if ASTRA_DB_COLLECTION not in collection_names:
                logger.info(f"Creating new collection: {ASTRA_DB_COLLECTION}")
                self.collection = self.db.create_collection(
                    collection_name=ASTRA_DB_COLLECTION,
                    dimension=384  # Dimension of the sentence-transformers embeddings
                )
            else:
                logger.info(f"Using existing collection: {ASTRA_DB_COLLECTION}")
                self.collection = self.db.get_collection(ASTRA_DB_COLLECTION)

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
            document_id = str(uuid.uuid4())

            # Convert numpy array to list if needed
            if hasattr(vector, 'tolist'):
                vector = vector.tolist()

            # Prepare document data
            document_data = {
                "text": text,
                "timestamp": datetime.now().isoformat()
            }

            # Add metadata if provided
            if metadata:
                document_data.update(metadata)

            # Insert document
            self.collection.insert_one(
                document_id=document_id,
                document=document_data,
                vector=vector
            )

            logger.info(f"Successfully stored vector with ID: {document_id}")
            return document_id
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
            results = self.collection.vector_search(
                vector=vector,
                limit=limit
            )

            # Process results to match expected format
            processed_results = []
            for result in results:
                # Add the similarity score to the document
                doc = result["document"]
                doc["_id"] = result["id"]
                doc["$similarity"] = result["similarity"]
                processed_results.append(doc)

            logger.info(f"Found {len(processed_results)} similar documents")
            return processed_results
        except Exception as e:
            logger.error(f"Error searching similar vectors in AstraDB: {str(e)}")
            return []

    def delete_document(self, document_id):
        """Delete a document from AstraDB"""
        if not self.is_connected:
            logger.error("Not connected to AstraDB")
            return False

        try:
            self.collection.delete_one(document_id)
            logger.info(f"Successfully deleted document with ID: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document from AstraDB: {str(e)}")
            return False

    def get_document(self, document_id):
        """Get a document from AstraDB by ID"""
        if not self.is_connected:
            logger.error("Not connected to AstraDB")
            return None

        try:
            result = self.collection.find_one(document_id)
            if result:
                # Format the result to match expected format
                doc = result["document"]
                doc["_id"] = document_id
                logger.info(f"Successfully retrieved document with ID: {document_id}")
                return doc
            else:
                logger.warning(f"Document with ID {document_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error getting document from AstraDB: {str(e)}")
            return None

# Create a singleton instance
astra_db_manager = AstraDBManager()

def get_astra_db_manager():
    """Get the AstraDB manager instance"""
    return astra_db_manager
