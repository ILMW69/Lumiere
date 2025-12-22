# 🧠 Semantic Memory System

The Semantic Memory System provides long-term conversational memory for Lumiere agents using vector-based semantic search.

## 🎯 Overview

Every time Lumiere successfully answers a question (ACCEPT decision), the conversation is automatically stored in a vector database. Later conversations can retrieve relevant past interactions to provide context-aware responses.

## 🏗️ Architecture

```
User Query → Intent Agent → Retriever/SQL → Reasoner → Critic
                                                          ↓
                                                      ACCEPT?
                                                          ↓
                                              Memory Write Node
                                                          ↓
                                              Qdrant Vector Store
                                              (agent_memories collection)
```

## 💾 How It Works

### 1. **Automatic Storage** (Memory Write Node)

When the critic makes an **ACCEPT** decision:

```python
# In graph/rag_graph.py - memory_write_node
if decision == "ACCEPT" and session_id:
    store_conversation_memory(
        query=query,
        response=answer,
        mode=mode,
        success=True,
        user_id=user_id,
        session_id=session_id
    )
```

**What's stored:**
- User's query (text)
- Agent's response (text)
- Mode used (`all_in`, `chat_rag`, `data_analyst`)
- Timestamp
- Session ID
- User ID (if provided)
- Success status

### 2. **Memory Retrieval**

Memories are retrieved using semantic search:

```python
# In agents/intent_agent.py
memories = retrieve_memories(
    query=user_input,
    user_id=user_id,
    top_k=3
)
```

**Process:**
1. User query is embedded (OpenAI text-embedding-3-small)
2. Vector search in Qdrant finds similar past conversations
3. Top-K most relevant memories returned
4. Formatted into context for the agent

### 3. **Context Integration**

Retrieved memories are added to agent prompts:

```python
📚 Relevant Past Context:

1. [CONVERSATION] (relevance: 0.95)
   Previous Query: "What is RAG?"
   Response: "RAG stands for Retrieval-Augmented Generation..."
   
2. [CONVERSATION] (relevance: 0.87)
   Previous Query: "How does vector search work?"
   Response: "Vector search uses embeddings to find similar content..."
```

## 🔧 Configuration

### Vector Database

**Collection**: `agent_memories`
**Vector Size**: 1536 (OpenAI ada-002 dimensions)
**Distance Metric**: Cosine similarity

### Storage Settings

```python
# memory/semantic_memory.py
MEMORY_COLLECTION_NAME = "agent_memories"
VECTOR_SIZE = 1536
```

### Retrieval Settings

Default retrieval parameters:
- **top_k**: 3 memories
- **score_threshold**: 0.7 (70% similarity minimum)
- **user_filtering**: Enabled (only retrieves user's own memories)

## 📊 Memory Metadata

Each memory stores:

```python
{
    "query": str,           # User's original question
    "response": str,        # Agent's response
    "mode": str,            # Lumiere mode used
    "success": bool,        # Whether interaction succeeded
    "timestamp": str,       # ISO format datetime
    "session_id": str,      # Conversation session
    "user_id": str,         # User identifier
    "memory_type": str,     # Always "conversation"
}
```

## 🎯 Use Cases

### 1. **Follow-up Questions**
```
User: "What is machine learning?"
Agent: [Explains ML and stores memory]

User: "Can you give me an example?"
Agent: [Retrieves previous explanation, provides relevant example]
```

### 2. **Cross-Session Continuity**
```
Session 1:
User: "Analyze the sales data for Q3"
Agent: [Performs analysis, stores result]

Session 2 (days later):
User: "What was our Q3 performance again?"
Agent: [Retrieves past analysis, provides summary]
```

### 3. **Learning User Preferences**
```
Multiple sessions:
User: "Show me the data as a bar chart"
Agent: [Creates bar chart, stores preference]

Later:
User: "Visualize the new dataset"
Agent: [Retrieves preference, automatically uses bar chart]
```

## 🚀 API Reference

### `store_conversation_memory()`

Store a conversation in semantic memory.

```python
def store_conversation_memory(
    query: str,
    response: str,
    mode: str,
    success: bool,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> str:
    """
    Store a conversation interaction.
    
    Args:
        query: User's query text
        response: Agent's response text
        mode: Mode used (all_in, chat_rag, data_analyst)
        success: Whether interaction succeeded
        user_id: Optional user identifier for filtering
        session_id: Optional session identifier
        **kwargs: Additional metadata
        
    Returns:
        Memory ID (UUID)
    """
```

**Example:**
```python
memory_id = store_conversation_memory(
    query="What is RAG?",
    response="RAG stands for Retrieval-Augmented Generation...",
    mode="chat_rag",
    success=True,
    user_id="user123",
    session_id="session456"
)
```

### `retrieve_memories()`

Retrieve relevant memories for a query.

```python
def retrieve_memories(
    query: str,
    user_id: Optional[str] = None,
    top_k: int = 3,
    score_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Retrieve semantically similar memories.
    
    Args:
        query: Search query text
        user_id: Filter by user (recommended)
        top_k: Number of memories to return
        score_threshold: Minimum similarity score
        
    Returns:
        List of memory dictionaries with scores
    """
```

**Example:**
```python
memories = retrieve_memories(
    query="Tell me about RAG",
    user_id="user123",
    top_k=5
)

for mem in memories:
    print(f"Score: {mem['score']:.2f}")
    print(f"Query: {mem['query']}")
    print(f"Response: {mem['response']}")
```

### `format_memories_for_context()`

Format memories for LLM context.

```python
def format_memories_for_context(
    memories: List[Dict[str, Any]]
) -> str:
    """
    Format memories into string for agent prompts.
    
    Args:
        memories: List of memory dictionaries
        
    Returns:
        Formatted string with emoji indicators
    """
```

## 🔍 Viewing Memories

### Streamlit UI

Memories are visible in the Streamlit sidebar:

1. **Memory Counter**: Shows total memories for current user
2. **Memory Viewer**: Expandable section showing recent memories
3. **Search**: Filter memories by content
4. **Delete**: Remove individual memories (if implemented)

### Qdrant Dashboard

Access Qdrant's web UI to inspect memories:

```bash
# If running locally
http://localhost:6333/dashboard
```

### Programmatic Access

```python
from memory.semantic_memory import retrieve_memories

# Get all memories for user
all_memories = retrieve_memories(
    query="",  # Empty query
    user_id="user123",
    top_k=100,
    score_threshold=0.0  # No filtering
)

print(f"Total memories: {len(all_memories)}")
```

## 🛠️ Troubleshooting

### Memory Not Storing

**Symptoms**: Memory count stays at 0 or doesn't increase

**Check:**
1. ✅ Critic is making ACCEPT decisions
2. ✅ `session_id` is present in state
3. ✅ `memory_write_node` is being called
4. ✅ Qdrant is running and accessible

**Debug:**
```python
# In graph/rag_graph.py - memory_write_node
print(f"💾 Memory write: decision={decision}, session={session_id}")
```

### Memory Retrieval Issues

**Symptoms**: No relevant memories returned

**Check:**
1. ✅ User has stored memories
2. ✅ `user_id` matches stored memories
3. ✅ Query similarity threshold not too high
4. ✅ Embeddings working correctly

**Debug:**
```python
# Test retrieval
memories = retrieve_memories(
    query="test",
    user_id="your_user_id",
    top_k=10,
    score_threshold=0.0  # Lower threshold
)
print(f"Found {len(memories)} memories")
```

### Collection Not Found

**Symptoms**: `Collection 'agent_memories' not found`

**Solution:**
```python
from memory.semantic_memory import create_memory_collection

create_memory_collection()
```

## 📈 Performance Considerations

### Scaling

- **Vector Search**: O(log n) with HNSW index (fast even with millions of memories)
- **Embedding**: ~100ms per query (OpenAI API latency)
- **Storage**: ~2-5KB per memory

### Optimization Tips

1. **Limit top_k**: Don't retrieve more than 5-10 memories
2. **Use score_threshold**: Filter low-quality matches
3. **User filtering**: Always filter by user_id
4. **Batch embeddings**: Embed multiple queries together

## 🔐 Privacy & Data Management

### User Isolation

Memories are isolated by `user_id`:
- Users only see their own memories
- No cross-user data leakage
- Filtering enforced at database level

### Data Retention

Current implementation stores memories indefinitely. To implement retention:

```python
# Delete old memories (example)
def prune_old_memories(user_id: str, days: int = 30):
    """Delete memories older than N days."""
    cutoff = datetime.now() - timedelta(days=days)
    # Implementation needed
```

### GDPR Compliance

To delete a user's data:

```python
from memory.semantic_memory import delete_user_memories

delete_user_memories(user_id="user123")
```

## 🚀 Future Enhancements

### Planned Features

- [ ] Memory summarization (condense old memories)
- [ ] Memory importance scoring
- [ ] Memory categories (facts, preferences, history)
- [ ] Cross-user shared knowledge base
- [ ] Memory export/import
- [ ] Memory editing
- [ ] Automatic memory pruning

### Advanced Use Cases

- **User profiling**: Learn long-term preferences
- **Knowledge graphs**: Connect related memories
- **Temporal reasoning**: Understand time-based patterns
- **Multi-modal memories**: Store images, charts, code

## 📚 Related Documentation

- [Graph Architecture](GRAPH_ARCHITECTURE.md) - How memory fits into workflow
- [Quick Start](QUICKSTART.md) - Getting started with Lumiere
- [Contributing](CONTRIBUTING.md) - How to contribute improvements

## 🤝 Contributing

Ideas for improving semantic memory:

1. Add memory categories
2. Implement memory importance scoring
3. Add memory search UI
4. Create memory analytics dashboard
5. Optimize embedding performance

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Questions?** Check the [main README](../README.md) or open an issue!
