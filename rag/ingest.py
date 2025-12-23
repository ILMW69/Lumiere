from uuid import uuid4
from rag.chunking import chunk_text
from rag.embeddings import embed_text
from rag.qdrant_client import get_client
from rag.collections import create_user_collection, get_user_collection_name
import time

def ingest_text(text: str, doc_id: str, user_id: str, retry_count: int = 3):
    """
    Ingest text into user-specific collection with retry logic.
    
    Args:
        text: Text to ingest
        doc_id: Document identifier
        user_id: User identifier for collection isolation
        retry_count: Number of retry attempts on network failure
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
    
    # Retry logic for network issues
    last_error = None
    for attempt in range(retry_count):
        try:
            client = get_client()
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            return len(points)
        except Exception as e:
            last_error = e
            if attempt < retry_count - 1:
                print(f"Ingest attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Failed to ingest after {retry_count} attempts: {e}")
                raise Exception(f"Failed to store in Qdrant after {retry_count} attempts: {str(e)}") from e
    
    # This shouldn't be reached, but just in case
    raise Exception(f"Failed to store in Qdrant: {str(last_error)}")