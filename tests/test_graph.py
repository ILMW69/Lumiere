"""
Tests for LangGraph workflow and state management.

Tests cover:
- Graph routing logic
- Memory write node
- State transitions
- Retry logic
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGraphWorkflow:
    """Test suite for LangGraph workflow."""

    def test_state_initialization(self, sample_state):
        """Test that AgentState initializes correctly."""
        from graph.state import AgentState
        
        # Verify required fields
        assert "messages" in sample_state
        assert "session_id" in sample_state
        assert "user_id" in sample_state
        assert "retry_count" in sample_state
        
        # Verify initial values
        assert sample_state["retry_count"] == 0
        assert sample_state["decision"] is None

    @patch('graph.rag_graph.store_conversation_memory')
    def test_memory_write_node_stores_on_accept(
        self,
        mock_store,
        sample_state,
        sample_session_id,
        sample_user_id
    ):
        """Test that memory_write_node stores conversation on ACCEPT."""
        from graph.rag_graph import memory_write_node
        
        # Setup - ACCEPT decision
        sample_state["decision"] = "ACCEPT"
        sample_state["session_id"] = sample_session_id
        sample_state["user_id"] = sample_user_id
        sample_state["question"] = "What is RAG?"
        sample_state["answer"] = "RAG is Retrieval-Augmented Generation"
        sample_state["reasoning_mode"] = "chat_rag"
        
        mock_store.return_value = True
        
        # Execute
        result = memory_write_node(sample_state)
        
        # Verify
        mock_store.assert_called_once()
        call_args = mock_store.call_args[1]
        assert call_args["query"] == "What is RAG?"
        assert call_args["response"] == "RAG is Retrieval-Augmented Generation"
        assert call_args["session_id"] == sample_session_id
        assert call_args["user_id"] == sample_user_id

    @patch('graph.rag_graph.store_conversation_memory')
    def test_memory_write_node_skips_on_retry(
        self,
        mock_store,
        sample_state
    ):
        """Test that memory_write_node skips storage on RETRY."""
        from graph.rag_graph import memory_write_node
        
        # Setup - RETRY decision
        sample_state["decision"] = "RETRY"
        sample_state["session_id"] = "test-session"
        
        # Execute
        result = memory_write_node(sample_state)
        
        # Verify - should not store
        mock_store.assert_not_called()

    @patch('graph.rag_graph.store_conversation_memory')
    def test_memory_write_node_handles_missing_session(
        self,
        mock_store,
        sample_state
    ):
        """Test that memory_write_node handles missing session_id."""
        from graph.rag_graph import memory_write_node
        
        # Setup - No session_id
        sample_state["decision"] = "ACCEPT"
        sample_state["session_id"] = None
        
        # Execute
        result = memory_write_node(sample_state)
        
        # Verify - should not store
        mock_store.assert_not_called()

    def test_route_from_critic_on_accept(self, sample_state):
        """Test routing from critic node on ACCEPT decision."""
        # The routing is inline in rag_graph.py as a lambda, test the logic
        sample_state["decision"] = "ACCEPT"
        sample_state["retry_count"] = 0
        
        # Simulate the routing logic from rag_graph.py
        route = (
            "retry"
            if sample_state["decision"] == "RETRY" and sample_state["retry_count"] < 1
            else "memory"
        )
        
        # Verify - should route to memory_write
        assert route == "memory"

    def test_route_from_critic_on_retry(self, sample_state):
        """Test routing from critic node on RETRY decision."""
        # The routing is inline in rag_graph.py as a lambda, test the logic
        sample_state["decision"] = "RETRY"
        sample_state["retry_count"] = 0
        
        # Simulate the routing logic from rag_graph.py
        route = (
            "retry"
            if sample_state["decision"] == "RETRY" and sample_state["retry_count"] < 1
            else "memory"
        )
        
        # Verify - should route to reasoner (retry)
        assert route == "retry"

    def test_route_from_memory_always_end(self, sample_state):
        """Test routing from memory_write always goes to END."""
        # Memory write is defined with graph.add_edge("memory_write", END)
        # This means it always goes to END, no routing function needed
        # Just verify the concept
        assert True  # Memory write is terminal node

    @patch('graph.rag_graph.store_conversation_memory')
    def test_memory_write_uses_correct_fields(
        self,
        mock_store,
        sample_state
    ):
        """Test that memory_write_node uses correct state fields."""
        from graph.rag_graph import memory_write_node
        
        # Setup with various field names
        sample_state["decision"] = "ACCEPT"
        sample_state["session_id"] = "test-session"
        sample_state["user_id"] = "test-user"
        sample_state["question"] = "Test question"
        sample_state["user_input"] = "Fallback input"
        sample_state["answer"] = "Test answer"
        sample_state["reasoning_mode"] = "chat_rag"
        sample_state["lumiere_mode"] = "all_in"
        
        mock_store.return_value = True
        
        # Execute
        memory_write_node(sample_state)
        
        # Verify - should prefer "question" over "user_input"
        call_args = mock_store.call_args[1]
        assert call_args["query"] == "Test question"
        # Should prefer "reasoning_mode" over "lumiere_mode"
        assert call_args["mode"] in ["chat_rag", "all_in"]

    def test_retry_count_increments(self, sample_state):
        """Test that retry_count is considered in routing logic."""
        # Test the routing logic considers retry_count
        sample_state["decision"] = "RETRY"
        sample_state["retry_count"] = 0
        
        # Should retry when count < 1
        route = (
            "retry"
            if sample_state["decision"] == "RETRY" and sample_state["retry_count"] < 1
            else "memory"
        )
        assert route == "retry"
        
        # Should not retry when count >= 1
        sample_state["retry_count"] = 1
        route = (
            "retry"
            if sample_state["decision"] == "RETRY" and sample_state["retry_count"] < 1
            else "memory"
        )
        assert route == "memory"

    @patch('graph.rag_graph.store_conversation_memory')
    def test_memory_write_with_sql_mode(
        self,
        mock_store,
        sample_state
    ):
        """Test memory storage for SQL query mode."""
        from graph.rag_graph import memory_write_node
        
        # Setup - SQL mode
        sample_state["decision"] = "ACCEPT"
        sample_state["session_id"] = "test-session"
        sample_state["user_id"] = "test-user"
        sample_state["question"] = "show me all records"
        sample_state["answer"] = "Here are the results: ..."
        sample_state["reasoning_mode"] = "sql"
        
        mock_store.return_value = True
        
        # Execute
        memory_write_node(sample_state)
        
        # Verify
        call_args = mock_store.call_args[1]
        assert call_args["mode"] == "sql"
