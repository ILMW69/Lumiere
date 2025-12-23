from langfuse import Langfuse
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize Langfuse client (gracefully handle missing credentials)
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

if public_key and secret_key:
    try:
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
        print("✅ Langfuse initialized successfully")
    except Exception as e:
        print(f"⚠️ Warning: Failed to initialize Langfuse: {e}")
        langfuse = None
else:
    print("⚠️ Warning: Langfuse credentials not found. Observability disabled.")
    langfuse = None