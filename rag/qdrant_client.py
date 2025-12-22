from qdrant_client import QdrantClient
from config.settings import QDRANT_URL, QDRANT_API_KEY
import os
import streamlit as st

# Global client instance
_client = None

def get_client() -> QdrantClient:
    """
    Get or create Qdrant client instance.
    Supports dynamic reinitialization when user provides credentials via setup page.
    """
    global _client
    
    # Check if user provided credentials via session state (setup page)
    session_url = st.session_state.get('user_qdrant_url')
    session_key = st.session_state.get('user_qdrant_key')
    
    # Use session credentials if available, otherwise fall back to config
    url = session_url if session_url else QDRANT_URL
    api_key = session_key if session_key else QDRANT_API_KEY
    
    # Reinitialize if credentials changed or client doesn't exist
    if _client is None or (session_url and session_key):
        _client = QdrantClient(
            url=url,
            api_key=api_key,
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
