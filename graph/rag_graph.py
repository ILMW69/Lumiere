from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import AgentState
from graph.nodes import (
    intent_node,
    retrieval_node,
    reasoning_node,
    general_reasoning_node,
    critic_node,
    sql_execution_node,
    sql_reasoning_node_wrapper,
    visualization_node
)
from memory.session_memory import append_session_memory
from memory.semantic_memory import store_conversation_memory

def memory_write_node(state):
    """
    Write session memory and semantic memory for accepted answers.
    
    Stores both short-term (session) and long-term (semantic) memories
    to enable context-aware responses in future interactions.
    """
    decision = state.get("decision")
    memory_signal = state.get("memory_signal") or state.get("memory")
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    print(f"💾 Memory Write Node - Decision: {decision}, Has memory_signal: {memory_signal is not None}, Session: {session_id}")

    # Store memories for all ACCEPT decisions (with or without explicit memory_signal)
    if decision == "ACCEPT" and session_id:
        # Store in session memory (short-term) if there's an explicit memory_signal
        if memory_signal:
            append_session_memory(
                session_id=session_id,
                item=memory_signal
            )

        # Store in semantic memory (long-term)
        try:
            # Get query from available state fields
            query = state.get("question") or state.get("user_input", "")
            answer = state.get("answer", "")
            # Get mode from available state fields
            mode = state.get("reasoning_mode") or state.get("lumiere_mode", "unknown")
            
            print(f"💾 Storing semantic memory - Query: {query[:50] if query else '(empty)'}..., Mode: {mode}")
            
            # Get additional metadata
            metadata = {
                "agents_used": state.get("agents_used", []),
                "retry_count": state.get("retry_count", 0)
            }
            
            # Add mode-specific metadata
            if mode == "data_analyst":
                sql_results = state.get("sql_results", {})
                viz_config = state.get("visualization_config", {})
                metadata.update({
                    "chart_type": viz_config.get("chart_type"),
                    "sql_query": sql_results.get("sql", "")[:200],  # Truncate
                    "tables_accessed": ["cars", "customers", "sales"]  # Could extract from SQL
                })
            
            store_conversation_memory(
                query=query,
                response=answer,
                mode=mode,
                success=True,
                user_id=user_id,
                session_id=session_id,
                **metadata
            )
            print(f"✅ Stored semantic memory for session {session_id}")
        except Exception as e:
            print(f"⚠️  Failed to store semantic memory: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⏭️  Skipping memory storage - Decision: {decision}, Session ID: {session_id}")

    return state

def build_graph():
    graph = StateGraph(AgentState)

    # nodes
    graph.add_node("intent", intent_node)
    graph.add_node("retrieve", retrieval_node)
    graph.add_node("reason", reasoning_node)
    graph.add_node("general_reason", general_reasoning_node)
    graph.add_node("sql_execute", sql_execution_node)
    graph.add_node("sql_reason", sql_reasoning_node_wrapper)
    graph.add_node("visualize", visualization_node)  # NEW: visualization for data analyst mode
    graph.add_node("critic", critic_node)
    graph.add_node("memory_write", memory_write_node)

    # entry
    graph.set_entry_point("intent")

    # intent → conditional (RAG, SQL, or general)
    def intent_router(state):
        if state.get("needs_sql"):
            return "sql"
        elif state.get("needs_rag"):
            return "rag"
        else:
            return "no_rag"
    
    graph.add_conditional_edges(
        "intent",
        intent_router,
        {
            "sql": "sql_execute",
            "rag": "retrieve",
            "no_rag": "general_reason"
        }
    )

    # SQL path
    graph.add_conditional_edges(
        "sql_execute",
        lambda state: (
            "failed"
            if not state.get("sql_results", {}).get("success")
            else "success"
        ),
        {
            "failed": "general_reason",  # Fallback on SQL failure
            "success": "sql_reason"
        }
    )
    
    # After SQL reasoning, check if we should visualize (data analyst mode)
    def should_visualize_router(state):
        mode = state.get("lumiere_mode", "all_in")
        sql_results = state.get("sql_results", {})
        
        # Only visualize in data_analyst mode with successful results
        if mode == "data_analyst" and sql_results.get("success") and sql_results.get("data"):
            return "visualize"
        return "critic"
    
    graph.add_conditional_edges(
        "sql_reason",
        should_visualize_router,
        {
            "visualize": "visualize",
            "critic": "critic"
        }
    )
    
    graph.add_edge("visualize", "critic")

    # RAG path
    graph.add_conditional_edges(
        "retrieve",
        lambda state: (
            "empty"
            if state.get("retrieved_docs") is None
            or len(state.get("retrieved_docs")) == 0
            else "found"
        ),
        {
            "empty": "general_reason",
            "found": "reason"
        }
    )
    graph.add_edge("general_reason", "critic")
    graph.add_edge("reason", "critic")

    # critic → decision
    # Always route through memory_write for ACCEPT decisions to store semantic memories
    graph.add_conditional_edges(
        "critic",
        lambda state: (
            "retry"
            if state["decision"] == "RETRY" and state["retry_count"] < 1
            else "memory"  # Always go to memory for non-retry (includes ACCEPT)
        ),
        {
            "retry": "reason",
            "memory": "memory_write",
        }
    )

    graph.add_edge("memory_write", END)

    # Add checkpointer to enable thread tracking in LangSmith
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)