from qdrant_client.models import VectorParams, Distance
from rag.qdrant_client import get_client


VECTOR_SIZE = 1536

def get_user_collection_name(user_id: str, collection_type: str = "documents") -> str:
    """
    Generate user-specific collection name.
    
    Args:
        user_id: Unique user identifier
        collection_type: Type of collection (documents or memories)
    
    Returns:
        User-specific collection name
    """
    # Sanitize user_id for collection name (Qdrant allows alphanumeric, underscore, hyphen)
    safe_user_id = user_id.replace("-", "_")
    return f"user_{safe_user_id}_{collection_type}"

def create_user_collection(user_id: str, collection_type: str = "documents"):
    """
    Create a user-specific collection if it doesn't exist.
    
    Args:
        user_id: Unique user identifier
        collection_type: Type of collection (documents or memories)
    """
    client = get_client()
    collection_name = get_user_collection_name(user_id, collection_type)
    
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {collection_name}")
    
    return collection_name