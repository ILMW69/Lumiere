import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, default=None):
    """Get environment variable from .env or Streamlit secrets."""
    value = os.getenv(key, default)
    if value is None:
        try:
            import streamlit as st
            value = st.secrets.get(key, default)
        except (ImportError, FileNotFoundError):
            pass
    return value

#OpenAI
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
LLM_MODEL = "gpt-5-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Qdrant
QDRANT_URL = get_env("QDRANT_URL")
QDRANT_API_KEY = get_env("QDRANT_API_KEY")
DOCUMENT_COLLECTION_NAME = "documents"
MEMORY_COLLECTION_NAME = "memories"

# RAG Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Langfuse
LANGFUSE_SECRET_KEY = get_env("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = get_env("LANGFUSE_PUBLIC_KEY")
LANGFUSE_BASE_URL = get_env("LANGFUSE_BASE_URL")