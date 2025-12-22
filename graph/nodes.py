from agents.intent_agent import intent_agent
from agents.reasoning_agent import reasoning_agent
from agents.critic_agent import critic_agent
from agents.query_reformulation_agent import reformulate_query
from rag.retriever import retrieve
from agents.general_reasoning_agent import general_reasoning_agent
from agents.sql_agent import text_to_sql
from agents.sql_reasoning_agent import sql_reasoning_agent
from agents.visualization_agent import visualization_agent

# 1. Intent node
def intent_node(state):
    return intent_agent(state)

# 2. Retrieval node
def retrieval_node(state):
    query = state.get("question") or state["messages"][-1]
    session_id = state.get("session_id")
    
    print(f"📦 Retrieval node - Session ID: {session_id}")
    
    # Reformulate query if it contains pronouns
    reformulated_query = reformulate_query(query, session_id)
    
    # Retrieve documents with reranking (top_k=5 for better coverage)
    docs = retrieve(reformulated_query, top_k=5, use_reranker=True, initial_k=20)
    
    # When using reranker, don't filter by score - reranker already sorted by relevance
    # Only use MIN_SCORE filter if NOT using reranker (vector scores are 0-1 range)
    # Since we're using reranker, trust the top_k results
    state["retrieved_docs"] = docs
    return state

# 3. Reasoning node
def reasoning_node(state):
    question = state.get("question") or state["messages"][-1]
    session_id = state.get("session_id")

    state["answer"] = reasoning_agent(
        question=question,
        retrieved_docs=state.get("retrieved_docs"),
        session_id=session_id,
    )
    state["reasoning_mode"] = "grounded"
    return state

# 4. Critic node
def critic_node(state):
    question = state.get("question") or state["messages"][-1]

    result = critic_agent(
        question=question,
        retrieved_docs=state.get("retrieved_docs"),
        answer=state.get("answer", ""),
        reasoning_mode=state.get("reasoning_mode"),
        user_input=state.get("user_input"),
    )

    # Unpack critic result
    decision = result.get("decision")
    memory_signal = result.get("memory_signal") or result.get("memory")

    state["decision"] = decision
    state["memory_signal"] = memory_signal

    if decision == "RETRY":
        state["retry_count"] += 1

    return state

# 5. General fallback reasoning node
def general_reasoning_node(state):
    question = state.get("question") or state["messages"][-1]
    session_id = state.get("session_id")

    state["answer"] = general_reasoning_agent(
        question=question,
        session_id=session_id,
    )
    state["reasoning_mode"] = "general"
    return state

# 6. SQL execution node
def sql_execution_node(state):
    """Execute SQL query from natural language."""
    question = state.get("question") or state["messages"][-1]
    
    print(f"🗄️  SQL execution node - Query: {question}")
    
    # Convert natural language to SQL and execute
    sql_results = text_to_sql(question)
    
    state["sql_results"] = sql_results
    state["sql_query"] = sql_results.get("sql")
    
    return state

# 7. SQL reasoning node
def sql_reasoning_node_wrapper(state):
    """Generate natural language response from SQL results."""
    return sql_reasoning_agent(state)
# 8. Visualization node
def visualization_node(state):
    """Generate visualization configuration for SQL results in data analyst mode."""
    print(f"�� Visualization node - Generating chart configuration")
    return visualization_agent(state)
