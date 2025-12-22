from openai import OpenAI
from config.settings import EMBEDDING_MODEL

_client = None

def _get_client():
    """Lazy initialization of OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

def embed_text(text: str) -> list[float]:
    """Generates an embedding for the given text using the specified model."""
    client = _get_client()
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding