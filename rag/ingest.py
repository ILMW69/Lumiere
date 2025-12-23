from uuid import uuid4
from rag.chunking import chunk_text
from rag.embeddings import embed_text
from rag.qdrant_client import get_client
from rag.collections import create_user_collection, get_user_collection_name

def ingest_text(text: str, doc_id: str, user_id: str):
    """
    Ingest text into user-specific collection.
    
    Args:
        text: Text to ingest
        doc_id: Document identifier
        user_id: User identifier for collection isolation
    """
    # Ensure user collection exists
    collection_name = create_user_collection(user_id, "documents")
    
    chunks = chunk_text(text)
    points = []

    for idx, chunk in enumerate(chunks):
        vector = embed_text(chunk)

        points.append({
            "id": str(uuid4()),
            "vector": vector,
            "payload": {
                "doc_id": doc_id,
                "chunk_index": idx,
                "text": chunk,
                "user_id": user_id  # Store user_id in payload for additional filtering
            }
        })
    
    client = get_client()
    client.upsert(
        collection_name=collection_name,
        points=points
    )

    return len(points)