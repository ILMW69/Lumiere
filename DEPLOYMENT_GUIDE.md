# 🚀 Lumiere Deployment Guide

## Streamlit Cloud Deployment Checklist

### ✅ Pre-Deployment Requirements

#### 1. **API Keys & Credentials**
Make sure you have these ready for Streamlit Cloud secrets:

```toml
# .streamlit/secrets.toml (DO NOT COMMIT THIS FILE)

# OpenAI API Key
OPENAI_API_KEY = "sk-..."

# Qdrant Cloud
QDRANT_URL = "https://your-cluster.qdrant.io"
QDRANT_API_KEY = "your-qdrant-api-key"

# Langfuse (Observability)
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_HOST = "https://cloud.langfuse.com"
```

#### 2. **GitHub Repository**
- ✅ Repository: `kikomatchi/Lumiere`
- ✅ Branch: `main`
- ✅ All code committed and pushed

#### 3. **Dependencies**
All dependencies are in `requirements.txt`:
- ✅ `streamlit>=1.28.0`
- ✅ `plotly>=5.18.0` (for visualizations)
- ✅ `langchain`, `langgraph`, `langfuse`
- ✅ `qdrant-client`, `openai`
- ❌ `streamlit-cookies-manager` (REMOVED - caused blocking)

---

## 🔧 Streamlit Cloud Setup

### Step 1: Create New App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select:
   - **Repository:** `kikomatchi/Lumiere`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click "Deploy"

### Step 2: Configure Secrets

1. In Streamlit Cloud dashboard, go to **App Settings** → **Secrets**
2. Paste your secrets in TOML format (see above)
3. Click "Save"

### Step 3: Advanced Settings (Optional)

- **Python version:** 3.11 or 3.12 (recommended)
- **Memory:** Default (1 GB should be sufficient)

---

## 📋 Post-Deployment Testing

### Test Checklist

#### ✅ 1. User Authentication
- [ ] Enter user name in sidebar
- [ ] Verify user_id is generated consistently
- [ ] Check that user info displays correctly

#### ✅ 2. Document Upload (PDF)
- [ ] Upload a test PDF via quick upload
- [ ] Verify it appears in document count
- [ ] Go to Documents page and verify it's listed
- [ ] Try deleting the document

#### ✅ 3. CSV Upload & SQL
- [ ] Upload a test CSV via quick upload
- [ ] Verify it appears in table count
- [ ] Switch to Data Analytics mode
- [ ] Ask a SQL query (e.g., "show me the first 5 rows")
- [ ] Verify visualization appears

#### ✅ 4. Mode Switching
- [ ] Switch to **All-In Mode** - Test general knowledge question
- [ ] Switch to **Docs & Chat Mode** - Test document question
- [ ] Switch to **Data Analytics Mode** - Test SQL query

#### ✅ 5. Agent Workflow
- [ ] Enable "Show Agent Workflow" toggle
- [ ] Ask a question and verify workflow steps display
- [ ] Disable toggle and verify clean chat interface

#### ✅ 6. Session Management
- [ ] Click "Clear Chat History" - Verify messages cleared
- [ ] Click "New Session" - Verify new session_id generated
- [ ] Verify session stats update correctly

#### ✅ 7. Langfuse Observability
- [ ] Go to [cloud.langfuse.com](https://cloud.langfuse.com)
- [ ] Verify traces are being logged
- [ ] Check that `user_id` and `session_id` are tracked
- [ ] Verify trace hierarchy (intent → retrieve → reason → critic)

---

## 🐛 Common Issues & Solutions

### Issue 1: "No documents found" after upload
**Solution:** 
- Check Qdrant connection in secrets
- Verify user_id is set before upload
- Check collection creation logs

### Issue 2: SQL queries fail
**Solution:**
- Verify CSV was uploaded successfully
- Check SQLite database file exists in `/databases/`
- Ensure user_id matches between upload and query

### Issue 3: Langfuse traces not appearing
**Solution:**
- Verify Langfuse secrets are correct
- Check network connectivity
- Ensure `LANGFUSE_HOST` is set

### Issue 4: "Module not found" error
**Solution:**
- Check `requirements.txt` has all dependencies
- Redeploy app to reinstall packages
- Verify Python version compatibility

### Issue 5: Chat interface not rendering
**Solution:**
- Check for any `st.stop()` calls in code
- Verify session state initialization
- Look for errors in Streamlit Cloud logs

---

## 🔍 Monitoring & Debugging

### Streamlit Cloud Logs
1. Go to app dashboard
2. Click "Manage app" → "Logs"
3. Watch for:
   - Import errors
   - API connection errors
   - Memory warnings

### Langfuse Dashboard
Monitor:
- **Traces:** Request flow through agents
- **Generations:** LLM calls and costs
- **Users:** Track active users by `user_id`
- **Sessions:** Track conversation sessions

### Health Checks
- Qdrant connection status
- OpenAI API rate limits
- Disk space for SQLite databases

---

## 📊 Expected Behavior

### User Flow
1. User enters name → consistent `user_id` generated
2. User uploads PDF → stored in `user_{user_id}_documents` collection
3. User uploads CSV → stored in `lumiere_user_{user_id}.db`
4. User asks question → graph workflow executes
5. Agent classifies intent → routes to appropriate nodes
6. Answer generated and displayed
7. Memory stored for future context

### Data Isolation
- ✅ Each user has separate Qdrant collection
- ✅ Each user has separate SQLite database
- ✅ User data never mixed or leaked
- ✅ Same name = same data (consistent user_id)

### Mode Behavior

| Mode | RAG | SQL | General Knowledge | Visualization |
|------|-----|-----|-------------------|---------------|
| **All-In** | ✅ | ✅ | ✅ | ✅ |
| **Docs & Chat** | ✅ | ❌ | ❌ | ❌ |
| **Data Analytics** | ✅ | ✅ | ❌ | ✅ |

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ App loads without errors
- ✅ Users can enter name and get consistent ID
- ✅ PDF uploads work and appear in document list
- ✅ CSV uploads work and SQL queries execute
- ✅ All 3 modes function correctly
- ✅ Visualizations render in Data Analytics mode
- ✅ Langfuse traces appear in dashboard
- ✅ No blocking or hanging issues
- ✅ Session management works (clear/new session)
- ✅ Document/table deletion works

---

## 📝 Notes for Capstone Demo

### Key Features to Demonstrate
1. **User Isolation:** Show multiple users with different data
2. **Multi-Modal:** Demonstrate all 3 modes
3. **RAG Quality:** Upload relevant doc, ask specific question
4. **SQL Intelligence:** Natural language to SQL conversion
5. **Visualizations:** Auto-generated charts from data
6. **Agent Workflow:** Show transparent agent execution
7. **Memory:** Demonstrate conversation context
8. **Observability:** Show Langfuse trace hierarchy

### Demo Script
1. Log in as "demo_user_1"
2. Upload sample PDF (e.g., research paper)
3. Upload sample CSV (e.g., sales data)
4. Switch to All-In Mode
5. Ask: "What is this document about?"
6. Switch to Data Analytics Mode
7. Ask: "Show me sales by region as a bar chart"
8. Enable workflow toggle to show agent execution
9. Show Langfuse dashboard with traces
10. Log in as "demo_user_2" to show isolation

### Limitations to Mention
- ⚠️ Session-based user_id (no persistence across browser sessions)
- ⚠️ SQLite file storage (not scalable for production)
- ⚠️ In-memory session memory (lost on app restart)
- ✅ These are acceptable for capstone prototype

---

## 🔐 Security Notes

- ✅ API keys stored in Streamlit secrets (not in code)
- ✅ User data isolated per user_id
- ✅ SQL injection prevented (parameterized queries)
- ✅ Only SELECT queries allowed (no DROP/DELETE)
- ⚠️ User can access others' data by guessing user_id
  - **Mitigation:** For production, add authentication layer

---

## 🚀 Ready for Deployment!

Your Lumiere app is now ready to deploy to Streamlit Cloud. Follow the steps above and enjoy your multi-agent RAG system! 🎉

**Good luck with your capstone presentation!** 💡
