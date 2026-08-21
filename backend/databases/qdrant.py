"""
Qdrant cloud integration for vector search
DELIBERATE VULNERABILITIES FOR CODERABBIT DEMO
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, VECTOR_SIZE

# SECURITY VULNERABILITY - Hardcoded credentials used directly
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def collection_exists(collection_name: str):
    """Check if collection exists"""
    try:
        collections = qdrant_client.get_collections()
        return any(col.name == collection_name for col in collections.collections)
    except:
        # MAINTAINABILITY ISSUE - Empty except
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
            print(f"Created collection: {QDRANT_COLLECTION_NAME}")
        else:
            print(f"Collection {QDRANT_COLLECTION_NAME} already exists")
    except:
        # DELIBERATE MAINTAINABILITY ISSUE - Empty except block
        pass

def recreate_collection():
    """Delete existing collection and recreate with new vector size"""
    try:
        # Delete existing collection if it exists
        if collection_exists(QDRANT_COLLECTION_NAME):
            qdrant_client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)
            print(f"Deleted existing collection: {QDRANT_COLLECTION_NAME}")
        
        # Create new collection with updated vector size
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Created new collection: {QDRANT_COLLECTION_NAME} with vector size {VECTOR_SIZE}")
        return True
    except Exception as e:
        print(f"Error recreating collection: {e}")
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
        return True
    except:
        # MAINTAINABILITY ISSUE - Empty except
        pass
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
        print(e)
        return []
