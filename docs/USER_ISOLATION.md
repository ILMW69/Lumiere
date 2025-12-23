# User Data Isolation Architecture

## Overview

Lumiere implements complete user data isolation to ensure each user's documents, tables, and memories are stored separately and securely. This multi-tenant architecture prevents any cross-user data leakage while maintaining a seamless user experience.

## Architecture Components

### 1. User-Specific Qdrant Collections

Each user gets two separate vector collections in Qdrant Cloud:

#### Documents Collection
- **Naming Pattern**: `user_{user_id}_documents`
- **Purpose**: Stores PDF document chunks and embeddings
- **Vector Size**: 1536 (OpenAI text-embedding-3-small)
- **Distance Metric**: Cosine similarity
- **Auto-Created**: On first document upload

#### Memories Collection
- **Naming Pattern**: `user_{user_id}_memories`
- **Purpose**: Stores semantic memories (conversations, preferences, patterns)
- **Vector Size**: 1536 (OpenAI text-embedding-3-small)
- **Distance Metric**: Cosine similarity
- **Auto-Created**: On first memory storage

### 2. User-Specific SQLite Databases

Each user gets a separate SQLite database file:

#### Database Files
- **Naming Pattern**: `lumiere_user_{user_id}.db`
- **Storage Location**: `/databases/` directory (auto-created)
- **Purpose**: Stores CSV tables uploaded by the user
- **Isolation**: Complete schema isolation per user
- **Auto-Created**: On first CSV upload

### 3. User Identification

- **User ID**: UUID generated per session (`st.session_state.user_id`)
- **Session Persistent**: Maintained throughout user session
- **Analytics**: Tracked in Langfuse for user behavior analysis
- **Privacy**: No PII collected, only session UUID

## Implementation Details

### Modified Files

#### `rag/collections.py`
```python
def get_user_collection_name(user_id: str, collection_type: str) -> str:
    """Generate user-specific collection name"""
    safe_user_id = user_id.replace("-", "_")
    return f"user_{safe_user_id}_{collection_type}"

def create_user_collection(user_id: str, collection_type: str):
    """Create user collection if it doesn't exist"""
    # Auto-creates Qdrant collection with proper config
```

#### `database/sqlite_client.py`
```python
def get_user_client(user_id: str) -> SQLiteClient:
    """Get or create user-specific SQLite client"""
    return SQLiteClient(user_id=user_id)
```

#### `rag/retriever.py`
```python
def retrieve(query: str, user_id: str, top_k: int = 5, ...) -> list[dict]:
    """Retrieve from user-specific collection"""
    collection_name = get_user_collection_name(user_id, "documents")
    # Query only this user's collection
```

#### `agents/sql_agent.py`
```python
def text_to_sql(user_query: str, user_id: str) -> dict:
    """Query user-specific database"""
    db = get_user_client(user_id)
    # Execute queries on user's isolated database
```

#### `memory/semantic_memory.py`
```python
def store_memory(content: str, memory_type: str, user_id: str, ...) -> str:
    """Store in user-specific memory collection"""
    collection_name = create_user_collection(user_id, "memories")
    # Store in isolated collection
```

#### `graph/nodes.py`
```python
def retrieval_node(state):
    """Retrieval with user isolation"""
    user_id = state.get("user_id", "default_user")
    docs = retrieve(reformulated_query, user_id=user_id, ...)

def sql_execution_node(state):
    """SQL execution with user isolation"""
    user_id = state.get("user_id", "default_user")
    sql_results = text_to_sql(question, user_id)
```

#### `app.py`
```python
# State includes user_id
initial_state = {
    "messages": [user_input],
    "session_id": st.session_state.session_id,
    "user_id": st.session_state.user_id,  # Passed to all nodes
    ...
}

# Sidebar shows user-specific data
collection_name = get_user_collection_name(st.session_state.user_id, "documents")
db_client = get_user_client(st.session_state.user_id)
```

## Data Flow

### Document Upload Flow
```
User Uploads PDF
    ↓
generate user_id (UUID)
    ↓
extract_text_from_pdf(file)
    ↓
chunk_text(text)
    ↓
embed_text(chunks)
    ↓
create_user_collection(user_id, "documents")
    ↓
store in user_{user_id}_documents
```

### RAG Query Flow
```
User Asks Question
    ↓
get user_id from session_state
    ↓
pass user_id to graph state
    ↓
retrieval_node extracts user_id
    ↓
retrieve(query, user_id) called
    ↓
query user_{user_id}_documents only
    ↓
return results (isolated to user)
```

### CSV Upload Flow
```
User Uploads CSV
    ↓
get user_id from session_state
    ↓
parse_csv(file)
    ↓
get_user_client(user_id)
    ↓
create table in lumiere_user_{user_id}.db
    ↓
insert data (isolated to user)
```

### SQL Query Flow
```
User Asks SQL Question
    ↓
get user_id from session_state
    ↓
pass user_id to graph state
    ↓
sql_execution_node extracts user_id
    ↓
text_to_sql(question, user_id)
    ↓
query lumiere_user_{user_id}.db only
    ↓
return results (isolated to user)
```

## Security Guarantees

### ✅ Data Isolation
- **Vector Database**: Each user has separate Qdrant collections
- **Relational Database**: Each user has separate SQLite database files
- **No Cross-Talk**: Queries never access other users' data
- **Lazy Creation**: Collections/databases created only when needed

### ✅ Privacy
- **No PII**: Only session UUID stored
- **Ephemeral Sessions**: UUID regenerated on browser close
- **No User Authentication**: Stateless by design
- **Analytics Anonymized**: Langfuse tracks by UUID, not personal info

### ✅ Scalability
- **Horizontal Scaling**: Add more Qdrant nodes as needed
- **File-Based DB**: SQLite files scale linearly with users
- **Lazy Loading**: Resources created on-demand
- **Memory Efficient**: No global shared state

## Limitations & Considerations

### Current Limitations
1. **Session-Based**: User ID tied to browser session
2. **No Persistence**: Closing browser creates new user ID
3. **No User Accounts**: Stateless, no login/authentication
4. **File System**: SQLite databases stored locally (not cloud-native)

### Future Enhancements
- [ ] Add persistent user accounts with authentication
- [ ] Migrate SQLite to cloud-native database (PostgreSQL/MySQL)
- [ ] Implement user data export/import
- [ ] Add admin dashboard for user management
- [ ] Implement data retention policies
- [ ] Add user quota management

## Testing User Isolation

### Manual Testing
```python
# Test 1: Upload document as User A
# Open browser → Upload PDF → Note user_id
# Check collection: user_{user_id_A}_documents exists

# Test 2: Open incognito window (User B)
# Upload different PDF → Note different user_id
# Check collection: user_{user_id_B}_documents exists

# Test 3: Query documents
# User A should only see their own documents
# User B should only see their own documents
```

### Verification Queries
```python
# Check Qdrant collections
from rag.qdrant_client import get_client
client = get_client()
collections = client.get_collections()
# Should see multiple user_* collections

# Check SQLite databases
import os
db_files = os.listdir('databases/')
# Should see multiple lumiere_user_*.db files
```

## Migration Guide

### Migrating from Shared Collections

If you have existing data in shared collections:

1. **Backup Existing Data**
```bash
# Export Qdrant collections
# Export SQLite database
```

2. **Update Code**
```python
# Already done - system now uses user_id everywhere
```

3. **Reassign Data to Users**
```python
# If you want to migrate old data:
# 1. Assign all old data to a default user
# 2. Or distribute based on session logs
# 3. Or simply start fresh
```

## Monitoring & Debugging

### Qdrant Collections
```python
from rag.collections import get_user_collection_name

# List user collections
user_id = "some-uuid-here"
doc_collection = get_user_collection_name(user_id, "documents")
mem_collection = get_user_collection_name(user_id, "memories")
```

### SQLite Databases
```python
from database.sqlite_client import get_user_client

# Access user database
user_id = "some-uuid-here"
db = get_user_client(user_id)
tables = db.list_tables()
```

### Langfuse Analytics
```
# All traces now include:
- user_id (UUID)
- session_id (UUID)
- User isolation visible in dashboard
- Filter by user_id to see specific user's activity
```

## Performance Considerations

### Qdrant Performance
- **Collection Overhead**: Minimal (Qdrant handles many collections well)
- **Query Performance**: Same as single collection (isolated to user)
- **Index Size**: Linear with number of users

### SQLite Performance
- **File System**: One file per user (efficient for <1000 users)
- **Query Performance**: Same as single database (smaller per-user)
- **Backup**: Easy (one file = one user)

### Recommendations
- **< 1,000 users**: Current architecture works great
- **1,000 - 10,000 users**: Consider database connection pooling
- **> 10,000 users**: Migrate to cloud-native database (PostgreSQL)

## Summary

Lumiere's user isolation architecture provides:
- ✅ **Complete data privacy** between users
- ✅ **Scalable multi-tenant design**
- ✅ **Zero cross-user data leakage**
- ✅ **Simple, maintainable codebase**
- ✅ **Production-ready isolation**

Every user operates in their own sandbox with separate vector collections and relational databases, ensuring enterprise-grade data isolation.
