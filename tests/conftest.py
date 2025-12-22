"""
Pytest configuration and shared fixtures for Lumiere tests.
"""
import pytest
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "test-langfuse-public")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "test-langfuse-secret")
    monkeypatch.setenv("LANGFUSE_HOST", "https://test.langfuse.com")


@pytest.fixture
def sample_session_id():
    """Provide a sample session ID for testing."""
    return "test-session-123"


@pytest.fixture
def sample_user_id():
    """Provide a sample user ID for testing."""
    return "test-user-456"


@pytest.fixture
def sample_state():
    """Provide a sample AgentState for testing."""
    return {
        "messages": ["What is machine learning?"],
        "session_id": "test-session-123",
        "user_id": "test-user-456",
        "lumiere_mode": "all_in",
        "intent": None,
        "needs_rag": None,
        "needs_sql": None,
        "retrieved_docs": None,
        "sql_query": None,
        "sql_results": None,
        "visualization_config": None,
        "answer": None,
        "retry_count": 0,
        "decision": None,
        "reasoning_mode": None,
        "user_input": "What is machine learning?",
        "question": "What is machine learning?",
        "memory_signal": None,
    }


@pytest.fixture
def sample_conversation():
    """Provide sample conversation data for memory testing."""
    return {
        "query": "What is RAG?",
        "response": "RAG stands for Retrieval-Augmented Generation...",
        "mode": "chat_rag",
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def mock_qdrant_client(monkeypatch):
    """Mock Qdrant client for testing without actual database."""
    mock_client = MagicMock()
    
    # Mock collection listing
    mock_collection = Mock()
    mock_collection.name = "agent_memories"
    mock_client.get_collections.return_value.collections = [mock_collection]
    
    # Mock search results
    mock_client.search.return_value = []
    
    # Mock upsert
    mock_client.upsert.return_value = None
    
    # Mock count
    mock_client.count.return_value.count = 0
    
    return mock_client


@pytest.fixture
def mock_openai_embeddings(monkeypatch):
    """Mock OpenAI embeddings for testing."""
    def mock_embed(text: str):
        # Return a dummy 1536-dimensional vector
        return [0.1] * 1536
    
    return mock_embed


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    mock_response = Mock()
    mock_response.content = "This is a test response from the LLM."
    return mock_response
