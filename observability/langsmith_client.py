"""LangSmith observability client"""
import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith environment variables
langsmith_api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT", "lumiere")
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

langsmith_enabled = False

if langsmith_api_key:
    try:
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = langsmith_project
        os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint
        
        langsmith_enabled = True
        print(f"✅ LangSmith tracing enabled - Project: {langsmith_project}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to initialize LangSmith: {e}")
        langsmith_enabled = False
else:
    print("⚠️ Warning: LangSmith API key not found. Tracing disabled.")
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
