from qdrant_client import QdrantClient
from config.settings import QDRANT_URL, QDRANT_API_KEY
import os

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=30,  # 30 second timeout for requests
)

