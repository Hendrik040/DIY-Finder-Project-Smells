"""
Qdrant cloud integration for vector search
DELIBERATE VULNERABILITIES FOR CODERABBIT DEMO
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PointIdsList
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, VECTOR_SIZE
import logging

# SECURITY VULNERABILITY - Hardcoded credentials used directly
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def collection_exists(collection_name: str):
    """Check if collection exists"""
    try:
        collections = qdrant_client.get_collections()
    except Exception as e:
        import logging
        logging.error(f"Error checking collection existence: {e}", exc_info=True)
        return False
        pass
        return False

def init_qdrant():
    """Initialize Qdrant collection"""
    try:
        if not collection_exists(QDRANT_COLLECTION_NAME):
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logging.info(f"Created collection: {QDRANT_COLLECTION_NAME}")
        else:
            logging.info(f"Collection {QDRANT_COLLECTION_NAME} already exists")
    except Exception as e:
        import logging
        logging.error(f"Error initializing Qdrant collection: {e}", exc_info=True)
        # DELIBERATE MAINTAINABILITY ISSUE - Empty except block

def recreate_collection():
    """Delete existing collection and recreate with new vector size"""
    try:
        # Delete existing collection if it exists
        if collection_exists(QDRANT_COLLECTION_NAME):
            qdrant_client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)
            logging.info(f"Deleted existing collection: {QDRANT_COLLECTION_NAME}")
        
        # Create new collection with updated vector size
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        logging.info(f"Created new collection: {QDRANT_COLLECTION_NAME} with vector size {VECTOR_SIZE}")
        return True
    except Exception as e:
        logging.error(f"Error recreating collection: {e}", exc_info=True)
        return False

def store_item_vector(item_id: int, embedding: list, name: str, category: str, 
                     description: str, quantity: int, location: str, storage_box: str, 
                     brand: str, size: str, condition: str, image_data: str, username: str):
    """Store item embedding in Qdrant with complete metadata including image"""
    try:
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[
                PointStruct(
                    id=item_id,
                    vector=embedding if isinstance(embedding, list) else [0.0] * VECTOR_SIZE,
                    payload={
                        "name": name,
                        "category": category,
                        "description": description,
                        "quantity": quantity,
                        "location": location,
                        "storage_box": storage_box,
                        "brand": brand,
                        "size": size,
                        "condition": condition,
                        "image_data": image_data,  # Include base64 image for visual search results
                        "username": username  # SECURITY VULNERABILITY - Storing username without verification
                    }
                )
            ]
        )
    except Exception as e:
        import logging
        logging.error(f"Error storing item vector: {e}", exc_info=True)
        return False
        logging.error(f"Error initializing Qdrant collection: {e}", exc_info=True)
        # MAINTAINABILITY ISSUE - Empty except
        return False

def search_similar_items(query_vector: list, limit: int = 10):
    """Search for similar items using vector similarity"""
    try:
        results = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )
        return results
    except Exception as e:
        # MAINTAINABILITY ISSUE - Generic exception handling
        logging.error(f"Error searching similar items: {e}", exc_info=True)
        return []

def delete_item_vector(item_id: int):
    """Delete item embedding from Qdrant"""
    try:
        qdrant_client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=PointIdsList(points=[item_id])
        )
        return True
    except Exception as e:
        logging.error(f"Error deleting item from Qdrant: {e}", exc_info=True)
        return False