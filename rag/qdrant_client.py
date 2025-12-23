from qdrant_client import QdrantClient
from config.settings import QDRANT_URL, QDRANT_API_KEY
import os

# Global client instance - using admin-provided credentials
_client = None

def get_client() -> QdrantClient:
    """
    Get or create Qdrant client instance.
    Uses admin-provided credentials from config/secrets.
    """
    global _client
    
    if _client is None:
        _client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=60,  # 60 second timeout for requests
            prefer_grpc=False,  # Use HTTP/REST instead of gRPC
        )
    
    return _client

# For backwards compatibility, create default client
client = None
try:
    # Try to initialize with config values
    if QDRANT_URL and QDRANT_API_KEY:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=60,
            prefer_grpc=False,
        )
except Exception:
    # Client will be initialized later via get_client()
    pass
