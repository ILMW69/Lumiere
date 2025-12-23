# LangSmith Threads Configuration for Lumiere

**Date:** December 23, 2025  
**Version:** 1.0.0  
**Status:** ✅ Implemented

---

## What Are LangSmith Threads?

LangSmith **threads** (also called `thread_id`) allow you to group related runs together, typically representing a conversation or user session. This enables:

1. **Conversation Tracking**: See all queries from a single user session grouped together
2. **Debug Full Conversations**: Trace issues across multiple turns
3. **User Journey Analysis**: Understand how users interact with Lumiere over time
4. **Performance Metrics**: Measure latency and token usage per session

---

## Implementation in Lumiere

### Changes Made

We added thread metadata to **both** graph invocation methods:

#### 1. Streaming Execution (with workflow display)
```python
for output in st.session_state.graph.stream(
    initial_state,
    config={
        "metadata": {
            "thread_id": st.session_state.session_id,
            "user_id": st.session_state.user_id,
            "user_name": st.session_state.user_name,
            "lumiere_mode": st.session_state.lumiere_mode
        }
    }
):
```

#### 2. Direct Execution (without workflow display)
```python
final_state = st.session_state.graph.invoke(
    initial_state,
    config={
        "metadata": {
            "thread_id": st.session_state.session_id,
            "user_id": st.session_state.user_id,
            "user_name": st.session_state.user_name,
            "lumiere_mode": st.session_state.lumiere_mode
        }
    }
)
```

### Metadata Fields

| Field | Description | Example |
|-------|-------------|---------|
| `thread_id` | Unique session identifier (groups conversation turns) | `"a1b2c3d4-e5f6-..."` |
| `user_id` | Hashed user identifier (MD5 of username) | `"8f4e7a2b3c9d1e0f"` |
| `user_name` | User-provided name/ID | `"john_doe"` |
| `lumiere_mode` | Active mode during the query | `"all_in"`, `"chat_rag"`, `"data_analyst"` |

---

## How to View Threads in LangSmith

### Step 1: Access LangSmith Dashboard
1. Go to https://smith.langchain.com/
2. Navigate to your project: **lumiere**

### Step 2: Filter by Thread
1. Click on **"Filters"** in the runs table
2. Add filter: **Metadata** → **thread_id** → `[paste session_id]`
3. Click **Apply**

### Step 3: View Grouped Runs
All runs with the same `thread_id` will be displayed together, showing:
- The complete conversation history
- Each query-response pair
- Node execution details for each turn
- Cumulative token usage

### Step 4: Analyze User Sessions
You can also filter by:
- **user_id**: See all sessions from a specific user
- **user_name**: Human-readable user identification
- **lumiere_mode**: Compare performance across modes

---

## Benefits for Your Capstone

### 1. Conversation Context
```
Thread: a1b2c3d4-e5f6-...
├── Turn 1: "What is supervised learning?" (RAG)
├── Turn 2: "Can you simplify that?" (RAG with context)
├── Turn 3: "Show me customers from NY" (SQL)
└── Turn 4: "Create a bar chart of that" (Visualization)
```

### 2. Debug Multi-Turn Issues
If a follow-up question fails, you can see:
- What was asked in previous turns
- What context was available
- Why the intent classification changed

### 3. Performance Analysis
Track per-session metrics:
- Average response time
- Total tokens used
- Success rate (ACCEPT vs REJECT)
- Most common failure points

### 4. User Behavior Insights
- Which modes do users prefer?
- How long are typical sessions?
- What types of queries follow each other?
- Where do users abandon sessions?

---

## Testing Thread Configuration

### Test 1: Single Session
1. Open Lumiere: https://lumiereworkspace.streamlit.app/
2. Enter your name (e.g., "test_user_1")
3. Note the Session ID displayed in sidebar (e.g., `a1b2c3d4...`)
4. Ask 3-4 questions in sequence
5. Go to LangSmith → Filter by `thread_id: a1b2c3d4...`
6. **Expected**: See all 4 queries grouped together

### Test 2: Multiple Sessions
1. Click "🔄 New Conversation" button
2. Note the NEW Session ID (e.g., `f9e8d7c6...`)
3. Ask 2-3 questions
4. Go to LangSmith → Filter by `thread_id: f9e8d7c6...`
5. **Expected**: See only the new session's queries

### Test 3: Multiple Users
1. Clear browser cookies (or use incognito)
2. Enter a different name (e.g., "test_user_2")
3. Ask questions
4. Go to LangSmith → Filter by `user_id: [user_2_hash]`
5. **Expected**: See only queries from user 2

---

## Advanced: Querying Threads Programmatically

You can use the LangSmith SDK to query threads:

```python
from langsmith import Client

client = Client()

# Get all runs for a specific thread
runs = client.list_runs(
    project_name="lumiere",
    filter='eq(metadata_key, "thread_id", "a1b2c3d4-e5f6-...")'
)

for run in runs:
    print(f"Query: {run.inputs.get('question')}")
    print(f"Answer: {run.outputs.get('answer')}")
    print(f"Latency: {run.latency_ms}ms")
    print("---")
```

---

## Troubleshooting

### Issue 1: Threads Not Showing Up

**Symptom**: Runs appear in LangSmith but not grouped by thread

**Solution**:
1. Verify `LANGCHAIN_TRACING_V2=true` in environment
2. Check that `thread_id` appears in run metadata
3. Ensure session_id is not changing unexpectedly

**Debug**:
```python
# Add to app.py temporarily
st.write(f"DEBUG - Session ID: {st.session_state.session_id}")
st.write(f"DEBUG - User ID: {st.session_state.user_id}")
```

### Issue 2: Different Session IDs for Same User

**Symptom**: Each page refresh creates a new session

**Expected Behavior**: This is intentional! Each browser session = new `session_id`

**Workaround**: To persist sessions across page refreshes, store `session_id` in browser cookies (future enhancement)

### Issue 3: Metadata Not Appearing

**Symptom**: `thread_id` is `null` in LangSmith

**Solution**:
1. Verify the `config` parameter is being passed correctly
2. Check LangGraph version: `pip show langgraph` (need ≥0.2.0)
3. Ensure metadata dict keys are strings (not other types)

---

## Example LangSmith Queries

### Query 1: All runs from a user's session
```
Metadata: thread_id equals "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
```

### Query 2: All runs from a specific user
```
Metadata: user_name equals "john_doe"
```

### Query 3: All queries in "data_analyst" mode
```
Metadata: lumiere_mode equals "data_analyst"
```

### Query 4: Failed runs in a session
```
Metadata: thread_id equals "a1b2c3d4-e5f6-..."
AND Status: Failed
```

---

## Next Steps (Optional Enhancements)

### 1. Persistent Sessions (Future v1.1.0)
Store `session_id` in browser cookies to survive page refreshes:
```python
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(password="secret_key")
if cookies.ready():
    session_id = cookies.get("lumiere_session_id")
```

### 2. Session Analytics Dashboard (Future v1.2.0)
Create a dedicated page showing:
- Active sessions
- Session duration
- Queries per session
- Success rates by session

### 3. Thread-Based Recommendations (Future v2.0.0)
Use thread history to suggest:
- Related questions
- Follow-up queries
- Document recommendations

---

## Configuration Status

| Component | Status | Thread ID Source |
|-----------|--------|------------------|
| Graph Invocation (invoke) | ✅ Configured | `st.session_state.session_id` |
| Graph Streaming (stream) | ✅ Configured | `st.session_state.session_id` |
| Metadata: user_id | ✅ Included | `st.session_state.user_id` |
| Metadata: user_name | ✅ Included | `st.session_state.user_name` |
| Metadata: lumiere_mode | ✅ Included | `st.session_state.lumiere_mode` |
| LangSmith Dashboard | ✅ Ready | https://smith.langchain.com/ |

---

## Files Modified

1. **app.py** (lines 464-479, 509-519)
   - Added `config` parameter to `graph.stream()`
   - Added `config` parameter to `graph.invoke()`
   - Included thread metadata in both invocation methods

---

## Demo for Capstone Defense

During your defense, you can demonstrate threads by:

1. **Show LangSmith Dashboard**: Open during demo
2. **Ask Multiple Questions**: Show 3-4 related queries
3. **Switch to LangSmith**: Filter by the session's `thread_id`
4. **Highlight Grouping**: Point out all queries appear together
5. **Click Into a Run**: Show full conversation context
6. **Explain Value**: "This thread tracking enables debugging multi-turn conversations"

**Pro Tip**: Take a screenshot of a thread with 4-5 queries for your presentation slides. Show how context flows through the conversation.

---

## Summary

✅ **What We Did**: Added LangSmith thread configuration to both graph execution paths  
✅ **Thread ID**: Uses `session_id` from Streamlit session state  
✅ **Additional Metadata**: Includes `user_id`, `user_name`, and `lumiere_mode`  
✅ **Benefits**: Conversation tracking, debugging, user analytics, performance monitoring  
✅ **Testing**: Ready to test immediately on deployed app  
✅ **Capstone Value**: Demonstrates production observability practices  

**Your LangSmith threads are now fully configured! 🚀**

Go test it out at: https://lumiereworkspace.streamlit.app/
