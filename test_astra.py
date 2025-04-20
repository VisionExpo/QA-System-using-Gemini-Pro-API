"""
Test script for AstraDB connection
"""

import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Token file
TOKEN_FILE = "gorulevishal984@gmail.com-token.json"

# Try to load token from file
def load_astra_token():
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                token_data = json.load(f)
                logger.info(f"Successfully loaded AstraDB token from {TOKEN_FILE}")
                
                # Extract token
                token = token_data.get('token')
                logger.info(f"Token: {token[:10]}...")
                
                # For this example, we'll use a default endpoint
                endpoint = "https://api.astra.datastax.com/v2/namespaces/default_keyspace/collections"
                
                return token, endpoint
        else:
            logger.warning(f"AstraDB token file not found: {TOKEN_FILE}")
            return None, None
    except Exception as e:
        logger.error(f"Error loading AstraDB token: {str(e)}")
        return None, None

def main():
    # Load token
    token, endpoint = load_astra_token()
    
    if not token or not endpoint:
        logger.error("Failed to load AstraDB token")
        return
    
    # Try to import astrapy
    try:
        from astrapy.db import AstraDB
        logger.info("Successfully imported AstraDB")
        
        # Try to connect to AstraDB
        try:
            logger.info(f"Connecting to AstraDB with token: {token[:10]}...")
            logger.info(f"API endpoint: {endpoint}")
            
            db = AstraDB(
                api_endpoint=endpoint,
                token=token
            )
            
            # Try to create a collection
            collection = db.create_collection(
                collection_name="test_collection",
                dimension=384
            )
            
            logger.info(f"Successfully connected to AstraDB and created collection: {collection}")
        except Exception as e:
            logger.error(f"Error connecting to AstraDB: {str(e)}")
    except ImportError:
        logger.error("Failed to import AstraDB. Make sure astrapy is installed.")

if __name__ == "__main__":
    main()
