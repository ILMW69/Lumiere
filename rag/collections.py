from qdrant_client.models import VectorParams, Distance
from rag.qdrant_client import get_client
from config.settings import DOCUMENT_COLLECTION_NAME


VECTOR_SIZE = 1536

def create_document_collection():
    client = get_client()
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if DOCUMENT_COLLECTION_NAME in existing:
        return
    
    client.create_collection(
        collection_name=DOCUMENT_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )