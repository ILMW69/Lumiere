from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL
from memory.session_memory import get_session_memory

_llm = None

def _get_llm():
    """Lazy initialization of ChatOpenAI client."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
        )
    return _llm

QUERY_REFORMULATION_PROMPT = """
You are a query reformulation agent.

Your task: Reformulate the user's query to be more specific for document retrieval.

If the user's query contains pronouns like "that", "it", "this", "the topic":
1. Look at the conversation history
2. Identify what the pronoun refers to
3. Reformulate the query to replace the pronoun with the actual topic

Examples:
- Conversation: "User: What is RAG?" → "Assistant: [explains RAG]"
- Current query: "simplify that"
- Reformulated: "simplify RAG" or "what is RAG in simple terms"

- Conversation: "User: Tell me about Paris" → "Assistant: [explains Paris]"  
- Current query: "what about its population"
- Reformulated: "what is the population of Paris"

If the query is already specific (no pronouns), return it unchanged.

Conversation History:
{conversation_history}

Current Query:
{query}

Reformulated Query (just the query, no explanation):
"""

def reformulate_query(query: str, session_id: str) -> str:
    """
    Reformulate a query by resolving pronouns using conversation history.
    Returns the original query if reformulation isn't needed.
    """
    # If query doesn't contain common pronouns, return as-is
    query_lower = query.lower()
    pronouns = ["that", "it", "this", "those", "these", "its", "their", "them"]
    
    # Check if any pronoun is in the query
    query_words = query_lower.split()
    has_pronoun = any(pronoun in query_words for pronoun in pronouns)
    
    print(f"🔍 Query analysis: '{query}'")
    print(f"   Has pronoun: {has_pronoun}")
    print(f"   Words: {query_words}")
    
    if not has_pronoun:
        print("   ➡️  No pronoun detected, returning original query")
        return query
    
    # Get conversation history
    print(f"   Session ID: {session_id}")
    memory_items = get_session_memory(session_id) if session_id else []
    print(f"   Memory items retrieved: {len(memory_items)}")
    conversation_items = [m for m in memory_items if m["type"] == "conversation"]
    
    if not conversation_items:
        print("   ➡️  No conversation history, returning original query")
        return query
    
    print(f"   Found {len(conversation_items)} conversation items")
    
    # Format recent conversation
    recent = conversation_items[-6:]  # Last 3 exchanges
    conversation_history = "\n".join([m["content"] for m in recent])
    
    # Reformulate the query
    llm = _get_llm()
    response = llm.invoke(
        QUERY_REFORMULATION_PROMPT.format(
            conversation_history=conversation_history,
            query=query
        )
    )
    
    reformulated = response.content.strip()
    
    print(f"🔄 Query reformulation:")
    print(f"   Original: {query}")
    print(f"   Reformulated: {reformulated}")
    
    return reformulated
