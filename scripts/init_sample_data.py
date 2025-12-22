"""
Initialize sample data for demo purposes.
Run this script to populate the vector database with sample documents.
"""
from rag.qdrant_client import client
from rag.collections import ensure_collection_exists
from rag.chunking import chunk_text
from rag.embeddings import embed_text
from config.settings import DOCUMENT_COLLECTION_NAME
import uuid

SAMPLE_DOCUMENTS = [
    {
        "title": "RAG Explained",
        "content": """Retrieval-Augmented Generation (RAG) is an AI framework that combines information retrieval with text generation. 

How RAG Works:
1. Document Ingestion: Documents are split into chunks and embedded into vectors
2. Storage: Vector embeddings are stored in a vector database like Qdrant
3. Retrieval: When a user asks a question, relevant chunks are retrieved using semantic search
4. Generation: The LLM generates an answer using the retrieved context

Key Benefits:
- Up-to-date information without retraining
- Source attribution and transparency
- Reduced hallucinations
- Domain-specific knowledge integration

RAG is particularly useful for enterprise applications where accuracy and traceability are critical."""
    },
    {
        "title": "Multi-Agent Systems",
        "content": """Multi-agent systems in AI involve multiple specialized agents working together to solve complex problems.

Common Agent Types:
1. Intent Agent: Classifies user queries and routes to appropriate handlers
2. Retrieval Agent: Searches for relevant information from knowledge bases
3. Reasoning Agent: Generates answers based on retrieved context
4. Critic Agent: Validates the quality and accuracy of generated responses

Benefits of Multi-Agent Architecture:
- Separation of concerns and modularity
- Specialized optimization for each task
- Better error handling and validation
- Scalability and maintainability

LangGraph is a popular framework for building multi-agent workflows with state management."""
    },
    {
        "title": "Vector Databases",
        "content": """Vector databases are specialized databases designed to store and query high-dimensional vector embeddings.

Popular Vector Databases:
- Qdrant: Open-source with cloud offering
- Pinecone: Managed service with good performance
- Weaviate: GraphQL-based vector search
- Milvus: Scalable for large datasets

Key Features:
1. Similarity Search: Find vectors closest to a query vector using metrics like cosine similarity
2. Filtering: Combine vector search with metadata filters
3. Scalability: Handle millions to billions of vectors
4. Performance: Sub-second query times even at scale

Vector databases are essential for modern RAG applications and semantic search systems."""
    },
    {
        "title": "Semantic Memory in AI",
        "content": """Semantic memory in AI systems refers to the ability to store and retrieve meaningful information from past interactions.

Implementation Approaches:
1. Short-term Memory: Store conversation history in session state
2. Long-term Memory: Persist important information in vector databases
3. Episodic Memory: Remember specific past interactions and contexts

Benefits:
- Personalized user experiences
- Context continuity across sessions
- Learning from past mistakes
- Improved relevance over time

Lumiere implements semantic memory by storing successful Q&A pairs in a dedicated Qdrant collection."""
    }
]

def initialize_sample_data():
    """Initialize Qdrant with sample documents."""
    print("🚀 Initializing sample data...")
    
    # Ensure collection exists
    ensure_collection_exists(DOCUMENT_COLLECTION_NAME)
    
    # Check if data already exists
    collection_info = client.get_collection(DOCUMENT_COLLECTION_NAME)
    if collection_info.points_count > 0:
        print(f"✅ Collection already has {collection_info.points_count} points. Skipping initialization.")
        return
    
    # Process each sample document
    for doc in SAMPLE_DOCUMENTS:
        print(f"📄 Processing: {doc['title']}")
        
        # Chunk the content
        chunks = chunk_text(doc['content'])
        print(f"   Created {len(chunks)} chunks")
        
        # Embed and store each chunk
        for idx, chunk in enumerate(chunks):
            embedding = embed_text(chunk)
            
            point_id = str(uuid.uuid4())
            
            client.upsert(
                collection_name=DOCUMENT_COLLECTION_NAME,
                points=[{
                    "id": point_id,
                    "vector": embedding,
                    "payload": {
                        "text": chunk,
                        "doc_id": doc['title'].lower().replace(" ", "_"),
                        "chunk_index": idx,
                        "source": f"{doc['title']} (Sample Document)"
                    }
                }]
            )
        
        print(f"   ✅ Stored {len(chunks)} chunks for {doc['title']}")
    
    # Verify
    collection_info = client.get_collection(DOCUMENT_COLLECTION_NAME)
    print(f"\n✅ Sample data initialized! Total points: {collection_info.points_count}")
    print(f"You can now ask questions about: RAG, Multi-Agent Systems, Vector Databases, and Semantic Memory")

if __name__ == "__main__":
    initialize_sample_data()
