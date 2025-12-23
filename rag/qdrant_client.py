from qdrant_client import QdrantClient
from config.settings import QDRANT_URL, QDRANT_API_KEY
import os
import time

# Global client instance - using admin-provided credentials
_client = None

def get_client(retry_count: int = 3) -> QdrantClient:
    """
    Get or create Qdrant client instance with retry logic.
    Uses admin-provided credentials from config/secrets.
    
    Args:
        retry_count: Number of retry attempts on connection failure
    """
    global _client
    
    if _client is None:
        for attempt in range(retry_count):
            try:
                _client = QdrantClient(
                    url=QDRANT_URL,
                    api_key=QDRANT_API_KEY,
                    timeout=120,  # Increased to 120 second timeout
                    prefer_grpc=False,  # Use HTTP/REST instead of gRPC
                )
                # Test connection
                _client.get_collections()
                break
            except Exception as e:
                if attempt < retry_count - 1:
                    print(f"Qdrant connection attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                else:
                    print(f"Failed to connect to Qdrant after {retry_count} attempts: {e}")
                    raise
    
    return _client

# For backwards compatibility, create default client
client = None
try:
    # Try to initialize with config values
    if QDRANT_URL and QDRANT_API_KEY:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=120,  # Increased timeout
            prefer_grpc=False,
        )
except Exception as e:
    # Client will be initialized later via get_client()
    print(f"Initial Qdrant client creation failed: {e}")
    pass
