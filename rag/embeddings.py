from openai import OpenAI
from config.settings import EMBEDDING_MODEL

client = OpenAI()

def embed_text(text: str) -> list[float]:
    """Generates an embedding for the given text using the specified model."""
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding