"""
Semantic Memory System using Qdrant Vector Database

This module provides long-term memory capabilities for agents using
semantic search to retrieve relevant past interactions and learnings.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from qdrant_client.models import (
    VectorParams, 
    Distance, 
    PointStruct, 
    Filter, 
    FieldCondition, 
    MatchValue,
    MatchAny
)

from rag.qdrant_client import client
from rag.embeddings import embed_text


# Collection name for agent memories
MEMORY_COLLECTION_NAME = "agent_memories"
VECTOR_SIZE = 1536  # OpenAI ada-002 embedding size


def create_memory_collection():
    """
    Create the Qdrant collection for storing agent memories.
    Only creates if it doesn't already exist.
    """
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if MEMORY_COLLECTION_NAME in existing:
        print(f"✅ Memory collection '{MEMORY_COLLECTION_NAME}' already exists")
        return
    
    client.create_collection(
        collection_name=MEMORY_COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print(f"✅ Created memory collection '{MEMORY_COLLECTION_NAME}'")


def store_memory(
    content: str,
    memory_type: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a memory in the semantic memory system.
    
    Args:
        content: The main content to remember (will be embedded)
        memory_type: Type of memory (conversation, preference, fact, pattern, error)
        user_id: Optional user identifier
        session_id: Optional session identifier
        metadata: Additional metadata (mode, agents_used, chart_type, etc.)
    
    Returns:
        memory_id: Unique identifier for the stored memory
    """
    # Generate unique ID
    memory_id = str(uuid.uuid4())
    
    # Get embeddings
    vector = embed_text(content)
    
    # Build payload
    payload = {
        "memory_id": memory_id,
        "content": content,
        "memory_type": memory_type,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id or "anonymous",
        "session_id": session_id or "unknown"
    }
    
    # Add metadata if provided
    if metadata:
        payload.update(metadata)
    
    # Store in Qdrant
    client.upsert(
        collection_name=MEMORY_COLLECTION_NAME,
        points=[
            PointStruct(
                id=memory_id,
                vector=vector,
                payload=payload
            )
        ]
    )
    
    return memory_id


def retrieve_memories(
    query: str,
    top_k: int = 5,
    memory_types: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    min_score: float = 0.7,
    metadata_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant memories using semantic search.
    
    Args:
        query: The query to search for
        top_k: Number of memories to retrieve
        memory_types: Filter by memory types (e.g., ["conversation", "preference"])
        user_id: Filter by user ID (applied post-retrieval, may return fewer than top_k)
        min_score: Minimum similarity score (0-1)
        metadata_filter: Additional filters (e.g., {"mode": "data_analyst"})
    
    Returns:
        List of memory dictionaries with content and metadata
        
    Note:
        user_id filtering is done post-retrieval to avoid requiring Qdrant payload indexes.
        If you need strict user isolation, consider creating separate collections per user
        or creating a payload index for user_id in Qdrant.
    """
    # Get embeddings for query
    query_vector = embed_text(query)
    
    # Build filters
    must_conditions = []
    
    if memory_types:
        must_conditions.append(
            FieldCondition(
                key="memory_type",
                match=MatchAny(any=memory_types)
            )
        )
    
    # Skip user_id filter to avoid index requirement
    # User filtering can be done post-retrieval if needed
    # if user_id:
    #     must_conditions.append(
    #         FieldCondition(
    #             key="user_id",
    #             match=MatchValue(value=user_id)
    #         )
    #     )
    
    # Add metadata filters
    if metadata_filter:
        for key, value in metadata_filter.items():
            must_conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )
    
    # Build filter object
    query_filter = Filter(must=must_conditions) if must_conditions else None
    
    # Search Qdrant - use the older search method that should work
    try:
        # Try the v1.7+ search method
        from qdrant_client.models import QueryRequest
        results = client.search(
            collection_name=MEMORY_COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=min_score,
            query_filter=query_filter
        )
    except (AttributeError, TypeError):
        # Fallback for newer versions
        results = client.query_points(
            collection_name=MEMORY_COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            score_threshold=min_score,
            using=None,  # Use default vector
            query_filter=query_filter
        ).points
    
    # Format results
    memories = []
    for result in results:
        # Handle both search result types
        score = result.score if hasattr(result, 'score') else getattr(result, 'score', 1.0)
        payload = result.payload if hasattr(result, 'payload') else {}
        
        # Optional post-filter by user_id (since we can't use indexed filter)
        if user_id and payload.get("user_id") != user_id:
            continue
        
        memory = {
            "memory_id": result.id,
            "content": payload.get("content", ""),
            "memory_type": payload.get("memory_type", "unknown"),
            "score": score,
            "timestamp": payload.get("timestamp", ""),
            "metadata": payload
        }
        memories.append(memory)
    
    return memories


def format_memories_for_context(memories: List[Dict[str, Any]]) -> str:
    """
    Format retrieved memories into a string for agent context.
    
    Args:
        memories: List of memory dictionaries
    
    Returns:
        Formatted string for injection into agent prompts
    """
    if not memories:
        return ""
    
    context = "📚 Relevant Past Context:\n"
    for i, mem in enumerate(memories, 1):
        context += f"\n{i}. [{mem['memory_type'].upper()}] (relevance: {mem['score']:.2f})\n"
        context += f"   {mem['content']}\n"
        
        # Add useful metadata
        if mem['metadata'].get('mode'):
            context += f"   Mode: {mem['metadata']['mode']}\n"
        if mem['metadata'].get('chart_type'):
            context += f"   Chart: {mem['metadata']['chart_type']}\n"
    
    return context


def store_conversation_memory(
    query: str,
    response: str,
    mode: str,
    success: bool,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function to store a conversation interaction.
    
    Args:
        query: User's query
        response: Agent's response
        mode: Mode used (all_in, chat_rag, data_analyst)
        success: Whether the interaction was successful
        user_id: Optional user identifier
        session_id: Optional session identifier
        **kwargs: Additional metadata (agents_used, chart_type, etc.)
    
    Returns:
        memory_id
    """
    # Create summary content
    content = f"User Query: {query}\nAgent Response: {response[:200]}..."
    
    # Build metadata
    metadata = {
        "mode": mode,
        "success": success,
        "query": query,
        "response_preview": response[:500],
        **kwargs
    }
    
    return store_memory(
        content=content,
        memory_type="conversation",
        user_id=user_id,
        session_id=session_id,
        metadata=metadata
    )


def store_preference_memory(
    preference: str,
    category: str,
    user_id: Optional[str] = None,
    **kwargs
) -> str:
    """
    Store a user preference.
    
    Args:
        preference: The preference description
        category: Category (visualization, query_style, etc.)
        user_id: User identifier
        **kwargs: Additional metadata
    
    Returns:
        memory_id
    """
    content = f"User Preference: {preference}"
    
    metadata = {
        "category": category,
        **kwargs
    }
    
    return store_memory(
        content=content,
        memory_type="preference",
        user_id=user_id,
        metadata=metadata
    )


def store_pattern_memory(
    pattern_description: str,
    pattern_type: str,
    example: Optional[str] = None,
    **kwargs
) -> str:
    """
    Store a learned pattern (e.g., successful SQL query structure).
    
    Args:
        pattern_description: Description of the pattern
        pattern_type: Type (sql_pattern, visualization_pattern, etc.)
        example: Example of the pattern in use
        **kwargs: Additional metadata
    
    Returns:
        memory_id
    """
    content = f"Pattern: {pattern_description}"
    if example:
        content += f"\nExample: {example}"
    
    metadata = {
        "pattern_type": pattern_type,
        **kwargs
    }
    
    return store_memory(
        content=content,
        memory_type="pattern",
        metadata=metadata
    )


def get_memory_stats() -> Dict[str, Any]:
    """
    Get statistics about stored memories.
    
    Returns:
        Dictionary with memory statistics
    """
    try:
        collection_info = client.get_collection(MEMORY_COLLECTION_NAME)
        
        # Get sample points to analyze types
        sample = client.scroll(
            collection_name=MEMORY_COLLECTION_NAME,
            limit=100
        )
        
        memory_types = {}
        for point in sample[0]:
            mem_type = point.payload.get("memory_type", "unknown")
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
        
        return {
            "total_memories": collection_info.points_count,
            "vector_size": collection_info.config.params.vectors.size,
            "memory_types": memory_types
        }
    except Exception as e:
        return {"error": str(e)}


# Initialize collection on import
try:
    create_memory_collection()
except Exception as e:
    print(f"⚠️  Could not create memory collection: {e}")
