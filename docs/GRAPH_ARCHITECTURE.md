# Lumiere Graph Architecture

## Overview
Lumiere uses a LangGraph-based agentic workflow that supports multiple modes (RAG, SQL/Data Analysis, General Chat) with integrated semantic memory for context-aware interactions.

## Graph Visualization
See `graph_visualization.mmd` for the Mermaid diagram.

## Node Descriptions

### 🎯 Intent Classification Node
**Purpose**: Determines the type of query and routes to appropriate processing path

**Inputs**:
- User query from `messages[-1]`
- Session context
- Semantic memories (retrieved for context)

**Outputs**:
- `intent`: Classification of query type
- `needs_rag`: Boolean for document retrieval requirement
- `needs_sql`: Boolean for database query requirement
- `question`: Processed user query

**Routing Logic**:
- `needs_rag=true` → RAG Retrieval Node
- `needs_sql=true` → SQL Execution Node  
- Both false → General Reasoning Node

**Semantic Memory Integration**: Retrieves top 3 relevant memories before classification to understand user context and preferences.

---

### 📚 RAG Retrieval Node
**Purpose**: Performs semantic search in document collection

**Inputs**:
- `question`: User query
- `session_id`: For tracking

**Processing**:
- Resolves pronouns/references using conversation history
- Generates embedding for query
- Searches Qdrant document collection
- Returns top-k relevant documents

**Outputs**:
- `retrieved_docs`: List of relevant document chunks
- Empty list if no relevant docs found

**Routing Logic**:
- `retrieved_docs` has items → RAG Reasoning Node
- `retrieved_docs` is empty → General Reasoning Node

**External Systems**: Connects to Qdrant for document semantic search

---

### 🧠 RAG Reasoning Node
**Purpose**: Generates grounded answer using retrieved context

**Inputs**:
- `question`: User query
- `retrieved_docs`: Context from RAG retrieval
- Session conversation history

**Processing**:
- Formats retrieved documents as context
- Uses LLM with strict grounding instructions
- Generates answer based only on provided context
- Includes source attribution

**Outputs**:
- `answer`: Generated response
- `reasoning_mode`: Set to "grounded"

**Next Node**: Critic Agent (always)

---

### 💬 General Reasoning Node
**Purpose**: Handles queries that don't require RAG or SQL

**Inputs**:
- `question`: User query
- Session conversation history
- System context

**Processing**:
- Direct LLM invocation without external context
- Uses conversational AI capabilities
- Handles follow-ups, clarifications, general knowledge

**Outputs**:
- `answer`: Generated response
- `reasoning_mode`: Set to "general"

**Use Cases**:
- No relevant documents found
- SQL execution failed
- General conversation/greetings
- Meta-questions about the system

**Next Node**: Critic Agent (always)

---

### 🗄️ SQL Execution Node
**Purpose**: Executes database queries for data analysis

**Inputs**:
- `question`: User query requesting data
- Database schema information
- Session context

**Processing**:
- Generates SQL query using LLM
- Validates SQL syntax
- Executes against SQLite database
- Handles errors and edge cases

**Outputs**:
- `sql_query`: Generated SQL
- `sql_results`: Execution results with data
  - `success`: Boolean
  - `data`: Query results
  - `columns`: Column metadata
  - `error`: Error message (if failed)

**Routing Logic**:
- `success=true` → SQL Reasoning Node
- `success=false` → General Reasoning Node (fallback)

**External Systems**: Connects to SQLite database

---

### 📊 SQL Reasoning Node
**Purpose**: Interprets SQL results and generates natural language response

**Inputs**:
- `question`: Original user query
- `sql_results`: Data from SQL execution
- `sql_query`: The executed SQL

**Processing**:
- Analyzes query results
- Generates insights and summaries
- Formats data for presentation
- Identifies visualization opportunities

**Outputs**:
- `answer`: Natural language interpretation
- `reasoning_mode`: Set to "sql"

**Routing Logic**:
- `lumiere_mode="data_analyst"` AND has data → Visualization Node
- Otherwise → Critic Agent

---

### 📈 Visualization Node
**Purpose**: Generates chart configuration for data analyst mode

**Inputs**:
- `sql_results`: Data to visualize
- `question`: User query
- `answer`: SQL reasoning output

**Processing**:
- Analyzes data structure and query intent
- Determines optimal chart type (bar, line, pie, scatter)
- Generates Plotly chart configuration
- Extracts x-axis, y-axis, labels

**Outputs**:
- `visualization_config`: Chart configuration object
  - `chart_type`: Type of chart
  - `x_column`: X-axis data
  - `y_column`: Y-axis data
  - `title`: Chart title
  - `labels`: Axis labels

**Next Node**: Critic Agent (always)

---

### ⚖️ Critic Agent
**Purpose**: Validates answer quality and completeness

**Inputs**:
- `answer`: Generated response
- `question`: User query
- `retrieved_docs`: Context used (if RAG)
- `reasoning_mode`: How answer was generated

**Processing**:
- Evaluates answer relevance
- Checks factual grounding
- Assesses completeness
- Detects hallucinations
- Extracts memory signals from user input

**Outputs**:
- `decision`: "ACCEPT", "REJECT", or "RETRY"
- `reasoning`: Explanation of decision
- `memory_signal`: Extracted user preferences/facts (if any)

**Routing Logic**:
- `decision="RETRY"` AND `retry_count < 1` → RAG Reasoning Node (retry)
- Otherwise → Memory Write Node

---

### 💾 Memory Write Node
**Purpose**: Stores conversation and semantic memories

**Inputs**:
- `decision`: Critic's verdict
- `question`: User query
- `answer`: Generated response
- `session_id`: Session identifier
- `user_id`: User identifier (optional)
- `memory_signal`: Explicit memory from critic
- `reasoning_mode`/`lumiere_mode`: Interaction mode

**Processing**:
1. **Session Memory** (if memory_signal exists):
   - Stores explicit user preferences/declarations
   - Short-term context for current session

2. **Semantic Memory** (if decision="ACCEPT"):
   - Embeds conversation using OpenAI embeddings
   - Stores in Qdrant vector database
   - Adds metadata (mode, agents used, retry count)
   - For data_analyst mode: Includes SQL query and chart type

**Storage Format**:
```python
{
    "memory_id": "uuid",
    "type": "conversation",
    "content": "User asked: <query>\nAssistant responded: <answer>",
    "timestamp": "ISO 8601",
    "metadata": {
        "query": "<original query>",
        "mode": "rag/sql/general",
        "success": true,
        "agents_used": [...],
        "retry_count": 0,
        "chart_type": "bar",  # data_analyst only
        "sql_query": "SELECT...",  # data_analyst only
    }
}
```

**External Systems**: Stores to Qdrant semantic memory collection

**Next Node**: END (workflow complete)

---

## External Systems

### 🧠 Qdrant Vector Database
**Purpose**: Semantic memory and document storage

**Collections**:
1. **agent_memories** (1536 dimensions)
   - Stores conversation memories
   - User preferences and facts
   - Query patterns
   - Error resolutions

2. **documents** (1536 dimensions)
   - RAG document chunks
   - Metadata and source attribution

**Operations**:
- **Intent Node**: Retrieves relevant memories for context
- **Retrieval Node**: Searches documents for RAG
- **Memory Write Node**: Stores new conversation memories

**Why Qdrant?**
- Fast vector similarity search
- Supports metadata filtering
- Scalable for growing memory banks
- Perfect for semantic search use cases

### 💾 SQLite Database
**Purpose**: Data source for SQL queries

**Usage**:
- SQL Execution Node queries for data analysis
- Supports multiple tables (cars, customers, sales, etc.)
- Lightweight, file-based database
- Read-only access from Lumiere for safety

---

## Workflow Paths

### Path 1: RAG Query
```
START → Intent (needs_rag=true) → Retrieve → Reason → Critic → Memory Write → END
```

**Example**: "What is FFXIV?"

**Memory Stored**:
- Query: "What is FFXIV?"
- Response: Retrieved document content
- Mode: "grounded"

---

### Path 2: SQL/Data Analysis Query
```
START → Intent (needs_sql=true) → SQL Execute → SQL Reason → [Visualize] → Critic → Memory Write → END
```

**Example**: "Show me the top 5 products by sales"

**Memory Stored**:
- Query: "Show me the top 5 products by sales"
- Response: Natural language summary of data
- Mode: "sql" or "general"
- Metadata: SQL query, chart type (if visualized)

---

### Path 3: General Chat
```
START → Intent (no flags) → General Reason → Critic → Memory Write → END
```

**Example**: "Hello, how are you?"

**Memory Stored** (if ACCEPT):
- Query: "Hello, how are you?"
- Response: Greeting response
- Mode: "general"

---

### Path 4: Failed Retrieval/SQL
```
START → Intent → [Retrieve/SQL Execute] → (fails) → General Reason → Critic → Memory Write → END
```

**Fallback behavior**: When specialized nodes fail, system gracefully falls back to general reasoning.

---

### Path 5: Retry Loop
```
START → Intent → Retrieve → Reason → Critic (RETRY) → Reason → Critic → Memory Write → END
```

**Trigger**: Critic rejects answer due to quality issues
**Limit**: Maximum 1 retry (retry_count < 1)

---

## Semantic Memory Benefits

### 1. **Context Awareness**
- System remembers past interactions
- Understands user preferences
- Provides personalized responses

### 2. **Learning from Interactions**
- Stores successful query patterns
- Remembers error resolutions
- Adapts to user communication style

### 3. **Cross-Session Continuity**
- Memories persist beyond single session
- User returns and system recalls preferences
- Long-term relationship building

### 4. **Quality Filtering**
- Only ACCEPT decisions stored
- Poor responses not remembered
- Clean, high-quality memory bank

### 5. **Mode-Specific Metadata**
- SQL queries stored for pattern learning
- Visualization preferences remembered
- RAG effectiveness tracked

---

## Configuration

### Memory Settings
```python
# Semantic memory retrieval (in intent_agent.py)
TOP_K = 3  # Number of memories to retrieve
MIN_SCORE = 0.75  # Similarity threshold

# Memory types supported
MEMORY_TYPES = [
    "conversation",  # General interactions
    "preference",    # User preferences
    "fact",         # User-declared facts
    "pattern",      # Query patterns
    "error_resolution"  # Problem solutions
]
```

### Graph Settings
```python
# Retry limit
MAX_RETRIES = 1

# Modes
LUMIERE_MODES = [
    "all_in",      # All features enabled
    "chat_rag",    # RAG + general chat only
    "data_analyst" # SQL + visualization
]
```

---

## Future Enhancements

### Potential Improvements
1. **Dynamic Memory Pruning**: Remove low-quality or outdated memories
2. **Memory Clustering**: Group related memories for better retrieval
3. **User Feedback Loop**: Allow users to correct/refine stored memories
4. **Multi-User Separation**: Better user_id filtering with Qdrant indexes
5. **Memory Analytics**: Track most useful memories, retrieval patterns
6. **Adaptive Top-K**: Dynamically adjust number of memories retrieved
7. **Memory Consolidation**: Merge similar memories to reduce redundancy

---

## Monitoring & Observability

### Key Metrics to Track
- Memory retrieval frequency and effectiveness
- Critic ACCEPT/REJECT rates per mode
- Retry rates and patterns
- Average memories per session
- Memory growth rate
- Query latency by path

### Debug Features
- Debug logging in memory_write_node
- Terminal emoji indicators (💾, ✅, ⏭️)
- Streamlit memory viewer UI
- Memory search and statistics

---

## Conclusion

Lumiere's graph architecture provides:
- ✅ **Multi-modal support** (RAG, SQL, General)
- ✅ **Semantic memory** for context-aware interactions
- ✅ **Quality assurance** via critic agent
- ✅ **Graceful fallbacks** for error handling
- ✅ **Extensible design** for future enhancements

The integration of semantic memory transforms Lumiere from a stateless QA system into an intelligent assistant that learns and adapts to user needs over time.
