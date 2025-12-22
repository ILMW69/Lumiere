from uuid import uuid4
from rag.chunking import chunk_text
from rag.embeddings import embed_text
from rag.qdrant_client import client
from config.settings import DOCUMENT_COLLECTION_NAME

def ingest_text(text: str, doc_id: str):
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
                "text": chunk
            }
        })
    client.upsert(
        collection_name=DOCUMENT_COLLECTION_NAME,
        points=points
    )

    return len(points)