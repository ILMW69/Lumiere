from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # input
    messages: List[str]

    # session context
    session_id: Optional[str]
    user_id: Optional[str]
    lumiere_mode: Optional[str]  # NEW: "all_in", "chat_rag", "rag_sql"

    # intent
    intent: Optional[str]
    needs_rag: Optional[bool]
    needs_sql: Optional[bool]  # NEW: SQL query detection

    # retrieval
    retrieved_docs: Optional[List[dict]]
    
    # SQL
    sql_query: Optional[str]  # NEW: Generated SQL
    sql_results: Optional[dict]  # NEW: SQL execution results

    # Visualization
    visualization_config: Optional[dict]  # NEW: Chart configuration for data analyst mode

    # reasoning
    answer: Optional[str]

    # control
    retry_count: int
    decision: Optional[str]

    reasoning_mode: Optional[str]  # e.g., "grounded", "general", "sql"
    
    # internal
    user_input: Optional[str]
    question: Optional[str]
    memory_signal: Optional[dict]
