# Lumiere Graph Architecture

## Overview
Lumiere uses a **9-node LangGraph workflow** with conditional routing, supporting multiple modes (RAG, SQL/Data Analysis, General Chat) with integrated semantic memory for context-aware interactions. The system features automatic LangSmith tracing for complete observability.

## Graph Visualization

**Current Architecture Diagram:**
- See `../lumiere_graph.mmd` and `../lumiere_graph.png` for the latest 9-node architecture
- Legacy diagram: `graph_visualization.mmd` (older version)

**Interactive Visualization:**
Visit https://mermaid.live and paste the content from `lumiere_graph.mmd` to view an interactive diagram with color-coded nodes.

## Complete Node List (9 Nodes)

1. **intent** - Intent classification and routing
2. **retrieve** - Vector search with reranking
3. **reason** - RAG-based reasoning
4. **general_reason** - General knowledge fallback
5. **sql_execute** - SQL generation and execution
6. **sql_reason** - SQL result interpretation
7. **visualize** - Plotly chart generation (data_analyst only)
8. **critic** - Answer quality evaluation
9. **memory_write** - Session + semantic memory storage

## Node Descriptions

### 🎯 Intent Node (Entry Point)
**Purpose**: Classifies user query, retrieves semantic memories, and determines routing path

**Inputs**:
- User query from `messages[-1]`
- `user_id`: For memory retrieval
- `mode`: Lumiere mode (all_in, chat_rag, data_analyst)
- Session context

**Processing**:
1. Retrieves top 3 relevant semantic memories for context
2. Analyzes query with memory context
3. Determines query intent and required resources

**Outputs**:
- `needs_rag`: Boolean for document retrieval requirement
- `needs_sql`: Boolean for database query requirement
- `user_query`: Processed/reformulated user query

**Routing Logic**:
- `mode='chat_rag'` → **retrieve** (forced RAG path)
- `mode='data_analyst'` → **sql_execute** (forced SQL path)
- `mode='all_in'`:
  - `needs_sql=True` → **sql_execute**
  - `needs_rag=True` → **retrieve**
  - Both false → **general_reason**

**Semantic Memory Integration**: Always retrieves memories before classification to provide personalized context.

---

### 📚 Retrieve Node
**Purpose**: Performs semantic search with CrossEncoder reranking

**Inputs**:
- `user_query`: User query (may be reformulated)
- `user_id`: For user-specific document collection

**Processing**:
1. Resolves pronouns/references using conversation history
2. Queries user-specific Qdrant collection: `user_{user_id}_documents`
3. Performs initial vector search (top-20 candidates)
4. Applies CrossEncoder reranking (ms-marco-MiniLM-L-6-v2)
5. Returns top-k most relevant documents

**Outputs**:
- `documents`: List[Document] with content and metadata
- Empty list if no relevant docs found

**Routing Logic**:
- `len(documents) > 0` → **reason**
- `len(documents) == 0` → **general_reason** (fallback)

**User Isolation**: Each user has separate Qdrant collection to prevent data leakage

**External Systems**: Qdrant Cloud vector database

---

### 🧠 Reason Node
**Purpose**: Generates grounded answer using retrieved RAG documents

**Inputs**:
- `user_query`: User question
- `documents`: Retrieved context from retrieve node
- `conversation_history`: Session messages
- `retry_count`: Number of retry attempts

**Processing**:
- Formats retrieved documents as context
- Uses gpt-4o-mini with strict grounding instructions
- Generates answer based only on provided context
- Includes source attribution

**Outputs**:
- `final_answer`: Generated response with sources
- `reasoning_mode`: Set to "grounded"

**Retry Capability**: Can be called again if critic decides RETRY (max 1 retry)

**Next Node**: **critic** (always)

---

### 💬 General Reason Node
**Purpose**: Handles queries without RAG or SQL, serves as fallback

**Inputs**:
- `user_query`: User question
- `conversation_history`: Session messages
- System context

**Processing**:
- Direct LLM invocation (gpt-4o-mini) without external context
- Uses conversational AI capabilities
- Handles follow-ups, clarifications, general knowledge
- Serves as fallback when SQL fails or no documents found

**Outputs**:
- `final_answer`: Generated response
- `reasoning_mode`: Set to "general"

**Use Cases**:
- No relevant documents found (retrieve → general_reason)
- SQL execution failed (sql_execute → general_reason)
- General conversation/greetings
- Meta-questions about the system

**Next Node**: **critic** (always)

---

### 🗄️ SQL Execute Node
**Purpose**: Generates and executes SQL queries on user-specific database

**Inputs**:
- `user_query`: User question requesting data
- `user_id`: For user-specific database
- Database schema information
- Session context

**Processing**:
- Generates SQL query using gpt-4o-mini
- Validates SQL syntax
- Executes against user's SQLite database (`lumiere_user_{user_id}.db`)
- Handles errors gracefully

**Outputs**:
- `sql_query`: Generated SQL statement
- `sql_result`: Execution results
  - Success: DataFrame with query results
  - Failure: Error message string

**Routing Logic**:
- `sql_result` is DataFrame (success) → **sql_reason**
- `sql_result` is error string (failure) → **general_reason** (fallback)

**User Isolation**: Each user has separate SQLite database

**External Systems**: SQLite database (`databases/lumiere_user_{user_id}.db`)

---

### 📊 SQL Reason Node
**Purpose**: Interprets SQL results and generates natural language response

**Inputs**:
- `user_query`: Original user question
- `sql_result`: DataFrame from sql_execute node
- `sql_query`: The executed SQL statement

**Processing**:
- Analyzes query results using gpt-4o-mini
- Generates insights and summaries
- Formats data for presentation
- Identifies visualization opportunities

**Outputs**:
- `final_answer`: Natural language interpretation of results
- `reasoning_mode`: Set to "sql"

**Routing Logic**:
- `mode='data_analyst'` AND `sql_result` has data → **visualize**
- Otherwise → **critic**

**Next Nodes**: **visualize** (conditional) or **critic**

---

### 📈 Visualize Node
**Purpose**: Generates Plotly chart configuration (data_analyst mode only)

**Inputs**:
- `sql_result`: DataFrame to visualize
- `user_query`: User question
- `final_answer`: SQL reasoning output

**Processing**:
- Analyzes data structure and query intent using gpt-4o-mini
- Determines optimal chart type (bar, line, pie, scatter, table)
- Generates Plotly chart configuration
- Extracts x-axis, y-axis, labels, and colors

**Outputs**:
- `visualization_result`: Plotly chart JSON configuration
  - `chart_type`: Type of chart
  - `x`: X-axis data column
  - `y`: Y-axis data column  
  - `title`: Chart title
  - `labels`: Axis labels
  - `config`: Full Plotly config

**Condition**: Only executed if `mode='data_analyst'` AND `sql_result` contains data

**Next Node**: **critic** (always)

---

### ⚖️ Critic Node
**Purpose**: Validates answer quality and determines if memory should be stored

**Inputs**:
- `final_answer`: Generated response
- `user_query`: User question
- `documents`: Context used (if RAG)
- `reasoning_mode`: How answer was generated (grounded/sql/general)

**Processing**:
- Evaluates answer relevance to query using gpt-4o-mini
- Checks factual grounding (for RAG mode)
- Assesses completeness
- Detects potential hallucinations
- Makes ACCEPT/RETRY decision

**Outputs**:
- `decision`: "ACCEPT" or "RETRY"
- `critic_reasoning`: Explanation of decision

**Routing Logic**:
- `decision='RETRY'` AND `retry_count < 1` → **reason** (retry once)
- `decision='ACCEPT'` OR `retry_count >= 1` → **memory_write**

**Quality Control**: Only ACCEPT decisions result in memory storage, ensuring clean memory bank

**Next Node**: **reason** (retry) or **memory_write**

---

### 💾 Memory Write Node (Terminal)
**Purpose**: Stores conversation in semantic memory (Qdrant) and session memory (SQLite)

**Inputs**:
- `decision`: Critic's verdict (ACCEPT/RETRY)
- `user_query`: User question
- `final_answer`: Generated response
- `session_id`: Session identifier
- `user_id`: User identifier
- `mode`: Interaction mode
- `reasoning_mode`: How answer was generated
- All state data for comprehensive storage

**Processing**:

**Session Memory** (SQLite):
- Stores turn-by-turn conversation
- User-specific database: `lumiere_user_{user_id}.db`
- Table: `session_memory`
- Always stored regardless of decision

**Semantic Memory** (Qdrant - only if ACCEPT):
1. Embeds conversation using OpenAI text-embedding-3-small
2. Stores in user's memory collection: `user_{user_id}_memories`
3. Adds comprehensive metadata:
   - `query`, `response`, `mode`, `reasoning_mode`
   - `timestamp`, `session_id`, `user_id`
   - `retry_count`, `agents_used`
   - For data_analyst: `sql_query`, `chart_type`

**Storage Format**:
```python
{
    "memory_id": "uuid",
    "type": "conversation",
    "content": "User: <query>\nAssistant: <answer>",
    "timestamp": "ISO 8601",
    "metadata": {
        "query": "<original query>",
        "response": "<answer>",
        "mode": "all_in|chat_rag|data_analyst",
        "reasoning_mode": "grounded|sql|general",
        "retry_count": 0,
        "session_id": "uuid",
        "user_id": "uuid",
        # data_analyst only:
        "sql_query": "SELECT...",
        "chart_type": "bar|line|pie|scatter"
    }
}
```

**External Systems**: 
- Qdrant Cloud (semantic memories)
- SQLite (session history)

**Next Node**: **END** (workflow complete)

---

## External Systems

### 🧠 Qdrant Cloud Vector Database
**Purpose**: Semantic memory and document storage with complete user isolation

**Collections** (per user):
1. **user_{user_id}_documents** (1536 dimensions)
   - Stores PDF/TXT/MD document chunks
   - Metadata: source, page, chunk_index
   - Used by: retrieve node

2. **user_{user_id}_memories** (1536 dimensions)
   - Stores conversation memories
   - Metadata: query, response, mode, timestamp, session_id
   - Used by: intent node (retrieval), memory_write node (storage)

**Operations**:
- **Intent Node**: Retrieves relevant memories for context (top-3)
- **Retrieve Node**: Searches documents for RAG with reranking
- **Memory Write Node**: Stores new conversation memories (ACCEPT only)

**User Isolation**: Each user has completely separate collections, preventing data leakage

**Why Qdrant Cloud?**
- Fast vector similarity search at scale
- Built-in metadata filtering
- Cloud-hosted with high availability
- Perfect for multi-tenant semantic search

### 💾 SQLite Database
**Purpose**: User-specific data storage for SQL queries and session memory

**Databases** (per user):
- **Filename**: `databases/lumiere_user_{user_id}.db`
- **Tables**: User-uploaded CSV tables (dynamic schema)
- **Session Memory**: `session_memory` table for conversation history

**Usage**:
- **SQL Execute Node**: Queries user's tables for data analysis
- **Memory Write Node**: Stores session-by-session conversation history
- **Sidebar Stats**: Retrieves table names and memory counts

**User Isolation**: Each user has completely separate database file

**Why SQLite?**
- Lightweight, file-based database
- No server setup required
- Perfect for per-user data isolation
- Supports full SQL capabilities

---

## Workflow Paths

### Path 1: RAG Query (Document Retrieval)
```
START → intent (needs_rag=true) → retrieve → reason → critic → memory_write → END
```

**Example**: "What features does the M2 have?" (with uploaded BMW docs)

**Flow**:
1. Intent node retrieves past memories, determines needs_rag=True
2. Retrieve node finds relevant document chunks from user's collection
3. Reason node generates grounded answer with sources
4. Critic evaluates quality, makes ACCEPT decision
5. Memory Write stores conversation in Qdrant + SQLite

**Memory Stored**:
- Query: "What features does the M2 have?"
- Response: Document-grounded answer with sources
- Mode: "chat_rag"
- Reasoning Mode: "grounded"

---

### Path 2: SQL/Data Analysis Query
```
START → intent (needs_sql=true) → sql_execute → sql_reason → [visualize] → critic → memory_write → END
```

**Example**: "Show me the top 5 cars by price"

**Flow**:
1. Intent node determines needs_sql=True
2. SQL Execute generates and runs: `SELECT * FROM cars ORDER BY price DESC LIMIT 5`
3. SQL Reason interprets results in natural language
4. Visualize creates chart (if data_analyst mode)
5. Critic evaluates, makes ACCEPT decision
6. Memory Write stores with SQL metadata

**Memory Stored**:
- Query: "Show me the top 5 cars by price"
- Response: Natural language summary + chart
- Mode: "data_analyst"
- Reasoning Mode: "sql"
- Metadata: sql_query, chart_type

---

### Path 3: General Chat
```
START → intent (no flags) → general_reason → critic → memory_write → END
```

**Example**: "Hello, how are you?"

**Flow**:
1. Intent node determines neither needs_rag nor needs_sql
2. General Reason provides conversational response
3. Critic makes ACCEPT decision
4. Memory Write stores conversation

**Memory Stored** (if ACCEPT):
- Query: "Hello, how are you?"
- Response: Conversational greeting
- Mode: "all_in"
- Reasoning Mode: "general"

---

### Path 4: Failed Retrieval/SQL (Fallback)
```
START → intent → [retrieve/sql_execute] → (fails) → general_reason → critic → memory_write → END
```

**Example**: RAG query with no relevant documents, or SQL execution error

**Flow**:
1. Intent routes to retrieve or sql_execute
2. Node fails (no docs or SQL error)
3. System falls back to general_reason
4. General Reason provides best-effort answer
5. Critic and Memory Write complete workflow

**Fallback Triggers**:
- `retrieve` returns empty documents → general_reason
- `sql_execute` returns error → general_reason

**Graceful Degradation**: System always provides a response, never fails completely

---

### Path 5: Retry Loop (Quality Control)
```
START → intent → retrieve → reason → critic (RETRY) → reason → critic → memory_write → END
```

**Example**: Initial answer is incomplete or hallucinated

**Flow**:
1. Normal RAG path: intent → retrieve → reason
2. Critic detects quality issue, decides RETRY
3. Reason node called again with retry_count=1
4. Critic re-evaluates second attempt
5. Force ACCEPT (max retry reached) → memory_write

**Trigger**: Critic detects issues like:
- Incomplete answers
- Potential hallucinations
- Not grounded in context

**Limit**: Maximum 1 retry (retry_count < 1), then force accept

---

### Mode-Specific Routing

#### Mode: **chat_rag**
- **Forces**: RAG path only
- **Path**: intent → retrieve → reason → critic → memory_write
- **Use Case**: Document-focused Q&A, knowledge base queries
- **Note**: Even if query could use SQL, forces RAG retrieval

#### Mode: **data_analyst**
- **Forces**: SQL + Visualization path
- **Path**: intent → sql_execute → sql_reason → visualize → critic → memory_write
- **Use Case**: Data analysis with automated charts
- **Note**: Always includes visualization step if data exists

#### Mode: **all_in** (Default)
- **Dynamic**: Intent agent decides path
- **Paths**: Any of RAG, SQL, or General
- **Use Case**: Flexible multi-modal queries
- **Logic**: Based on query analysis and available resources

---

## 📊 Observability with LangSmith

### Automatic Tracing

Lumiere uses **LangSmith** for complete observability without any manual instrumentation:

**Setup**:
- Environment variables configured in `observability/langsmith_client.py`
- Automatic tracing via `LANGCHAIN_TRACING_V2=true`
- All LangChain/LangGraph operations automatically traced

**What's Traced**:
- Every node execution with inputs/outputs
- LLM calls (prompts, completions, tokens)
- Vector searches (queries, results, scores)
- SQL queries (generation, execution, results)
- Routing decisions and conditional logic
- Error states and retry attempts

**Benefits**:
1. **Zero Code Changes**: No manual tracing code needed
2. **Complete Visibility**: Every operation is logged
3. **Performance Metrics**: Latency, tokens, costs per operation
4. **Debugging**: Full trace replay for debugging
5. **User Analytics**: Session tracking via user_id/session_id

**Configuration** (in `.env`):
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=Lumiere
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

**Dashboard Features**:
- Trace timelines with node-by-node execution
- Token usage and cost tracking
- Error rate monitoring
- Session grouping by user/session ID
- Performance bottleneck identification

**Why LangSmith over Langfuse?**
- Native LangChain/LangGraph integration
- Automatic instrumentation
- Better trace organization
- Simpler setup (no manual code)

See `LANGSMITH_GUIDE.md` for complete setup instructions.

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

### LLM Settings
```python
# All nodes use OpenAI gpt-4o-mini
MODEL = "gpt-4o-mini"
TEMPERATURE = 0  # Deterministic for consistency
MAX_TOKENS = 2000  # Adjustable per node

# Embeddings (Qdrant storage + retrieval)
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
```

### Memory Settings
```python
# Semantic memory retrieval (in intent node)
TOP_K_MEMORIES = 3  # Number of memories to retrieve
MIN_MEMORY_SCORE = 0.7  # Similarity threshold

# Document retrieval (in retrieve node)
TOP_K_DOCS = 5  # Final documents after reranking
RERANK_TOP_K = 20  # Candidates before reranking

# Memory storage
MEMORY_TYPES = ["conversation"]  # Future: preference, fact, pattern
```

### Graph Settings
```python
# Retry limit
MAX_RETRIES = 1  # Maximum retry attempts in critic loop

# Lumiere Modes
MODES = {
    "all_in": "Dynamic routing (SQL/RAG/General)",
    "chat_rag": "Force RAG path only",
    "data_analyst": "Force SQL + visualization"
}

# User isolation
USER_COLLECTION_PATTERN = "user_{user_id}_{type}"
USER_DATABASE_PATTERN = "lumiere_user_{user_id}.db"
```

### Routing Configuration
```python
# Intent routing (agents/intent_agent.py)
- chat_rag mode: Always needs_rag=True
- data_analyst mode: Always needs_sql=True
- all_in mode: LLM decides based on query

# Fallback triggers
- retrieve returns []: Route to general_reason
- sql_execute returns error: Route to general_reason

# Visualization condition
- Mode must be "data_analyst"
- sql_result must be DataFrame (not empty)

# Critic routing
- RETRY + retry_count < 1: Route to reason
- Otherwise: Route to memory_write
```

---

## Future Enhancements

### Planned Improvements

1. **Enhanced Memory Management**
   - Memory pruning: Remove low-quality or outdated memories
   - Memory consolidation: Merge similar conversations
   - Memory importance scoring: Prioritize valuable memories
   - Adaptive retrieval: Dynamically adjust top-k based on query

2. **Advanced Routing**
   - Hybrid queries: Support SQL + RAG in single query
   - Multi-step reasoning: Chain multiple node executions
   - Parallel execution: Run retrieve + sql_execute concurrently
   - Smart fallbacks: Contextual fallback strategies

3. **User Experience**
   - Streaming responses: Show partial results during generation
   - Confidence scores: Display answer confidence to users
   - Source highlighting: Show exact document excerpts used
   - Interactive refinement: Allow users to refine answers

4. **Data Analysis**
   - Multi-table JOINs: Complex SQL across tables
   - Data profiling: Automatic data quality analysis
   - Trend detection: Identify patterns in time-series
   - Export capabilities: Download charts and data

5. **Memory System**
   - Memory categories: Separate preference, fact, pattern memories
   - User feedback loop: Allow memory correction/deletion
   - Memory sharing: Share memories across related users (teams)
   - Memory analytics: Track most useful memories

6. **Observability**
   - Custom metrics: Track domain-specific KPIs
   - A/B testing: Compare prompt variations
   - Cost optimization: Monitor and reduce token usage
   - Performance alerts: Notify on latency spikes

7. **Security & Privacy**
   - Encryption at rest: Encrypt sensitive data
   - Access control: Role-based permissions
   - Audit logging: Track all data access
   - Data retention policies: Auto-delete old data

---

## Monitoring & Debugging

### LangSmith Dashboard

**Key Metrics**:
- Total traces per day/week
- Average latency per node
- Token usage and cost per operation
- Error rate by node type
- Retry frequency (critic → reason loops)
- Memory storage rate (ACCEPT vs RETRY ratio)

**Trace Analysis**:
- View full conversation context
- See exact prompts and responses
- Track routing decisions
- Identify slow nodes
- Debug error states

### Terminal Debug Indicators

Lumiere uses emoji indicators in terminal output:

```
🎯 Intent classification complete
📦 Retrieval node - Session ID: xxx, User ID: xxx
🔍 Query analysis: Has pronoun: False
💾 Memory Write Node - Decision: ACCEPT
✅ Stored semantic memory for session xxx
⏭️  Skipping memory write - Decision: RETRY
```

**Benefits**:
- Quick visual scan of workflow
- Easy debugging of routing
- Memory storage confirmation
- Error identification

### Sidebar Statistics

The Streamlit sidebar shows real-time stats:

```
🗄️ Database Info
└─ Tables: 3 (cars, sales, customers)
└─ Total Rows: 1,234

📚 Document Stats  
└─ Documents: 15
└─ Chunks: 243

🧠 Semantic Memory
└─ Conversations Stored: 67
└─ Search Memories
```

**Usage**:
- Monitor memory growth
- Track document ingestion
- Verify database tables
- Search stored memories

### Error Handling

**Graceful Failures**:
- SQL errors → fallback to general_reason
- No documents → fallback to general_reason
- LLM errors → retry with exponential backoff
- Qdrant errors → log and continue (session memory only)

**Error Logging**:
```python
logger.error(f"❌ Node failed: {error}")
logger.warning(f"⚠️  Fallback triggered")
logger.info(f"ℹ️  Alternative path taken")
```

---

## Conclusion

Lumiere's 9-node graph architecture provides:

✅ **Multi-modal Intelligence**
- RAG for document-grounded answers
- SQL for data analysis with visualization
- General chat for conversational AI
- Smart routing based on query intent

✅ **Semantic Memory System**
- Long-term learning from conversations
- Context-aware personalized responses
- Quality-filtered memory storage
- Cross-session continuity

✅ **User Data Isolation**
- Complete separation per user
- Dedicated Qdrant collections
- Individual SQLite databases
- Secure multi-tenant architecture

✅ **Quality Assurance**
- Critic-based validation
- Retry mechanism for poor answers
- Graceful fallback paths
- Error handling at every level

✅ **Complete Observability**
- Automatic LangSmith tracing
- Zero manual instrumentation
- Full trace replay for debugging
- Performance and cost monitoring

✅ **Production-Ready**
- Scalable with Qdrant Cloud
- Extensible node architecture
- Configurable routing logic
- Comprehensive error handling

The integration of semantic memory, user isolation, and automatic tracing transforms Lumiere from a stateless Q&A system into an **intelligent, personalized assistant that learns and adapts** to each user's needs over time.

For detailed implementation, see:
- `graph/rag_graph.py` - Graph definition
- `agents/` - Individual node implementations
- `memory/semantic_memory.py` - Memory operations
- `observability/langsmith_client.py` - Tracing setup

**Architecture Diagram**: See `../lumiere_graph.png` or `../lumiere_graph.mmd` for visual representation.
