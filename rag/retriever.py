from rag.qdrant_client import get_client
from rag.embeddings import embed_text
from config.settings import DOCUMENT_COLLECTION_NAME
from sentence_transformers import CrossEncoder

# Initialize Cross-Encoder for reranking
# Using MS MARCO MiniLM - fast and effective for semantic search
_reranker = None

def get_reranker():
    """Lazy load the reranker model to avoid loading at import time."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    return _reranker

def retrieve(query: str, top_k: int = 5, use_reranker: bool = True, initial_k: int = 20) -> list[dict]:
    """
    Retrieve relevant documents with optional reranking.
    
    Args:
        query: The search query
        top_k: Number of final results to return (default: 5)
        use_reranker: Whether to use Cross-Encoder reranking (default: True)
        initial_k: Number of candidates to retrieve before reranking (default: 20)
    
    Returns:
        List of retrieved documents with scores
        
    Note:
        When using reranker, scores can be negative (not 0-1 range).
        Reranker already sorts by relevance, so no need for MIN_SCORE filtering.
    """
    # Stage 1: Vector similarity search
    # Retrieve more candidates if using reranker, otherwise just get top_k
    retrieval_limit = initial_k if use_reranker else top_k
    
    query_vector = embed_text(query)

    client = get_client()
    results = client.query_points(
        collection_name=DOCUMENT_COLLECTION_NAME,
        query=query_vector,
        limit=retrieval_limit,
        with_payload=True
    ).points

    # Convert to list of dicts
    candidates = []
    for r in results:
        candidates.append(
            {
                "vector_score": r.score,  # Keep original vector score
                "doc_id": r.payload.get("doc_id"),
                "chunk_index": r.payload.get("chunk_index"),
                "text": r.payload.get("text"),
            }
        )
    
    # Stage 2: Reranking (optional)
    if use_reranker and len(candidates) > 0:
        reranker = get_reranker()
        
        # Create query-document pairs for Cross-Encoder
        pairs = [[query, doc["text"]] for doc in candidates]
        
        # Get reranking scores
        rerank_scores = reranker.predict(pairs)
        
        # Add rerank scores to candidates
        for doc, rerank_score in zip(candidates, rerank_scores):
            doc["rerank_score"] = float(rerank_score)
            doc["score"] = float(rerank_score)  # Use rerank score as primary score
        
        # Sort by rerank score (descending)
        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # Return top_k after reranking
        return candidates[:top_k]
    else:
        # No reranking - just use vector scores
        for doc in candidates:
            doc["score"] = doc["vector_score"]
        return candidates[:top_k]