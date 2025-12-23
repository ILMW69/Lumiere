from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL
from memory.session_memory import get_session_memory
from memory.semantic_memory import retrieve_memories, format_memories_for_context

# Initialize ChatOpenAI client at module load
llm = ChatOpenAI(
    model_name=LLM_MODEL,
    temperature=0,
)

INTENT_PROMPT = """
You are an intent classification agent for an AI knowledge workspace.

Your task:
1. Classify the user's intent
2. Decide whether document retrieval (RAG) is required
3. Decide whether SQL database query is required

CRITICAL: CHECK FOR SQL QUERIES FIRST!

SQL QUERY DETECTION (HIGHEST PRIORITY):
- If the question asks about DATA in tables, records, rows, statistics, filtering, aggregations → SET needs_sql to TRUE
- SQL Action Keywords: "show", "list", "count", "average", "mean", "sum", "total", "find", "get", "how many", "filter", "display", "retrieve", "search for"
- SQL Operations: counting, averaging, summing, filtering, sorting, grouping, finding max/min
- Question patterns: "what is the average...", "how many...", "show me...", "list all...", "find records where...", "get data about..."
- ANY query asking for numerical data, statistics, or listing of records → SQL
- If needs_sql is TRUE, set needs_rag to FALSE (SQL queries don't need document retrieval)

SQL Examples (SET needs_sql: true, needs_rag: false):
- "show me all records" → sql_query
- "what's the average of column X?" → sql_query
- "average price/salary/value of Y" → sql_query
- "how many items/rows are available" → sql_query
- "list all data in table" → sql_query
- "find records with value > 50000" → sql_query
- "count total rows/items" → sql_query
- "display top 10 by price/date" → sql_query
- "get all entries where status = X" → sql_query
- "sum of values in column" → sql_query

RAG/DOCUMENT QUERY DETECTION:
- If the question is about CONCEPTS, explanations, how-to, definitions → SET needs_rag to TRUE
- Document keywords: "explain", "what is", "how does", "describe", "definition", "tutorial", "guide"
- If asking about previous document-based answers → SET needs_rag to TRUE

RAG Examples (SET needs_rag: true, needs_sql: false):
- "explain to me about RAG" → question, needs_rag: true
- "what is machine learning?" → question, needs_rag: true
- "how does retrieval work?" → question, needs_rag: true

GENERAL CHAT:
- Greetings, casual conversation → SET both to FALSE

Valid intents:
- sql_query: User asking about data in tables (needs_sql: true, needs_rag: false)
- question: User asking conceptual questions (needs_rag: true, needs_sql: false)
- summarization: User wants a summary (needs_rag: true, needs_sql: false)
- general_chat: Casual conversation (needs_rag: false, needs_sql: false)
- context_declaration: User stating information (needs_rag: false, needs_sql: false)

Conversation History:
{conversation_history}

Current User Input:
{user_input}

IMPORTANT: If the query mentions data entities (employees, cars, prices, salaries, etc.) or asks for statistics/listings, classify as sql_query!

Respond ONLY in valid JSON (no markdown, no code blocks, just raw JSON):

{{
  "intent": "sql_query",
  "needs_rag": false,
  "needs_sql": true
}}
"""
def intent_agent(state):
    user_input = state["messages"][-1]
    session_id = state.get("session_id")
    lumiere_mode = state.get("lumiere_mode", "all_in")  # Get mode from state
    
    state["user_input"] = user_input
    state["question"] = user_input
    state["needs_sql"] = False  # Default
    
    # MODE-BASED INTENT OVERRIDE
    # This ensures intent classification respects the selected mode
    
    # Mode 2: Chat & RAG only (no SQL)
    if lumiere_mode == "chat_rag":
        state["needs_sql"] = False  # Force disable SQL
        # Continue with normal intent detection for RAG vs general chat
    
    # Mode 3: Data Analyst (RAG & SQL only, no general chat)
    if lumiere_mode == "data_analyst":
        # Force all queries to either RAG or SQL (no general reasoning)
        pass  # Will be handled by intent logic below

    lowered = user_input.lower()
    
    # Quick pre-check for context declarations
    if lowered.startswith(
        (
            "i am ",
            "i'm ",
            "i am building ",
            "i'm building ",
            "i am working on ",
            "i'm working on ",
            "i am developing ",
            "i'm developing ",
        )
    ):
        state["intent"] = "context_declaration"
        state["needs_rag"] = False
        state["needs_sql"] = False
        state["question"] = user_input
        return state
    
    # Quick pre-check for obvious SQL queries
    # Strong SQL action verbs and patterns
    sql_action_keywords = [
        "show", "list", "display", "get", "find", "retrieve",
        "count", "average", "sum", "total", "calculate",
        "how many", "how much", "what is the average", "what's the total"
    ]
    
    # Data indicators (more generic)
    data_indicators = [
        "all", "records", "rows", "entries", "items", "data",
        "table", "database", "where", "with", "by", "from"
    ]
    
    # Check if query contains SQL-related patterns
    has_sql_action = any(keyword in lowered for keyword in sql_action_keywords)
    has_data_indicator = any(indicator in lowered for indicator in data_indicators)
    
    # Aggregation/statistical keywords (strong SQL signals)
    has_aggregation = any(word in lowered for word in [
        "average", "mean", "sum", "total", "count", 
        "maximum", "minimum", "max", "min"
    ])
    
    # If has SQL action OR aggregation, it's very likely SQL
    if has_sql_action or has_aggregation:
        # Extra confirmation: check for data indicators or question patterns
        question_patterns = ["how many", "how much", "what is the", "show me", "list all"]
        has_question_pattern = any(pattern in lowered for pattern in question_patterns)
        
        if has_data_indicator or has_question_pattern or has_aggregation:
            # Check mode restrictions
            if lumiere_mode != "chat_rag":  # SQL allowed in all_in and data_analyst modes
                state["intent"] = "sql_query"
                state["needs_rag"] = False
                state["needs_sql"] = True
                return state

    # Get conversation history for context
    conversation_history = "No previous conversation."
    if session_id:
        memory_items = get_session_memory(session_id)
        conversation_items = [m for m in memory_items if m["type"] == "conversation"]
        if conversation_items:
            recent = conversation_items[-6:]  # Last 3 exchanges
            conversation_history = "\n".join([m["content"] for m in recent])
    
    # 🧠 NEW: Retrieve semantic memories
    semantic_context = ""
    try:
        user_id = state.get("user_id")
        relevant_memories = retrieve_memories(
            query=user_input,
            top_k=3,
            user_id=user_id,
            min_score=0.75
        )
        if relevant_memories:
            semantic_context = "\n\n" + format_memories_for_context(relevant_memories)
            print(f"🧠 Retrieved {len(relevant_memories)} relevant memories")
    except Exception as e:
        print(f"⚠️  Could not retrieve semantic memories: {e}")

    response = llm.invoke(
        INTENT_PROMPT.format(
            conversation_history=conversation_history + semantic_context,
            user_input=user_input
        )
    )
    content = response.content.strip()
    
    # Remove markdown code blocks if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    
    # Parse the response
    content_lower = content.lower()

    # Check for SQL intent (with mode restrictions)
    if '"needs_sql": true' in content_lower or '"needs_sql":true' in content_lower or "sql_query" in content_lower:
        # SQL only allowed in all_in and rag_sql modes
        if lumiere_mode != "chat_rag":
            state["needs_sql"] = True
            state["needs_rag"] = False
            state["intent"] = "sql_query"
        else:
            # In chat_rag mode, treat SQL queries as regular questions
            state["needs_sql"] = False
            state["needs_rag"] = True
            state["intent"] = "question"
    elif "summarization" in content_lower:
        state["intent"] = "summarization"
        state["needs_rag"] = True
        state["needs_sql"] = False
    elif "context_declaration" in content_lower:
        state["intent"] = "context_declaration"
        state["needs_rag"] = False
        state["needs_sql"] = False
    elif "general_chat" in content_lower:
        # In data_analyst mode, convert general chat to RAG (prevent hallucination)
        if lumiere_mode == "data_analyst":
            state["intent"] = "question"
            state["needs_rag"] = True
            state["needs_sql"] = False
        else:
            state["intent"] = "general_chat"
            state["needs_rag"] = False
            state["needs_sql"] = False
    else:
        # Default to question with RAG
        state["intent"] = "question"
        state["needs_sql"] = False
        # Check if needs_rag is explicitly set to false
        if '"needs_rag": false' in content_lower or '"needs_rag":false' in content_lower:
            # In data_analyst mode, force RAG even if LLM says no (prevent hallucination)
            if lumiere_mode == "data_analyst":
                state["needs_rag"] = True
            else:
                state["needs_rag"] = False
        else:
            state["needs_rag"] = True

    return state
