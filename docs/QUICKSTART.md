# 🚀 Quick Start Guide

Get Lumiere up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11 or higher installed
- [ ] Docker installed (for Qdrant)
- [ ] OpenAI API key ready
- [ ] 5 minutes of your time ⏰

## Step-by-Step Setup

### 1️⃣ Install Python Dependencies (2 min)

```bash
# Clone and enter directory
git clone https://github.com/yourusername/lumiere.git
cd lumiere

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt
```

### 2️⃣ Start Qdrant Vector Database (1 min)

```bash
# Run Qdrant in Docker
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    --name lumiere-qdrant \
    qdrant/qdrant

# Verify it's running
curl http://localhost:6333/health
# Should return: {"status":"ok"}
```

### 3️⃣ Configure Environment (1 min)

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
QDRANT_URL=http://localhost:6333
```

### 4️⃣ Initialize Collections (30 sec)

```bash
# Create Qdrant collections
python -c "from rag.collections import init_all_collections; init_all_collections()"

# Initialize semantic memory with sample data
python scripts/init_semantic_memory.py
```

You should see:
```
✅ Created collection 'documents'
✅ Created collection 'agent_memories'
✅ Seeded 3 initial memories
```

### 5️⃣ Launch Lumiere! (30 sec)

```bash
streamlit run app.py
```

🎉 **Open your browser to http://localhost:8501**

---

## First Steps After Launch

### 📄 Upload Your First Document

1. Click **"📄 Document Ingestion"** in the sidebar
2. Upload a PDF, TXT, or MD file
3. Click **"Ingest Documents"**
4. Wait for success message

### 💬 Ask Your First Question

Try these examples:

**RAG Query (uses your documents):**
```
What is discussed in the uploaded document?
```

**Data Analysis Query:**
```
Show me the top 5 cars by price
```

**General Chat:**
```
Hello! What can you help me with?
```

### 🧠 Check Semantic Memory

1. Expand **"🧠 Semantic Memory"** in sidebar
2. See how many conversations are stored
3. Try searching: `cars` or `database`

---

## Common First-Time Issues

### ❌ "Cannot connect to Qdrant"

**Check if Qdrant is running:**
```bash
docker ps | grep qdrant
```

**If not running:**
```bash
docker start lumiere-qdrant
```

**If doesn't exist, recreate:**
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    --name lumiere-qdrant \
    qdrant/qdrant
```

### ❌ "Invalid OpenAI API key"

1. Check your `.env` file
2. Verify the key is correct (starts with `sk-`)
3. Restart Streamlit after changing `.env`

### ❌ "No module named X"

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### ❌ Port already in use (8501)

```bash
# Use a different port
streamlit run app.py --server.port 8502
```

---

## Next Steps

### 📚 Learn More

- **[README.md](README.md)**: Full documentation
- **[GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md)**: How it works
- **[SEMANTIC_MEMORY.md](SEMANTIC_MEMORY.md)**: Memory system details

### 🎯 Try Advanced Features

1. **Data Analyst Mode**:
   - Switch mode in sidebar to "Data Analyst"
   - Ask: "Show me sales trends by month"
   - See automated visualizations!

2. **Semantic Memory**:
   - Ask multiple questions
   - Notice how responses become more context-aware
   - Check memory growth in sidebar

3. **Custom Documents**:
   - Ingest your own PDFs/documents
   - Ask questions about them
   - See source attribution in answers

### 🔧 Customize

- Edit `config/settings.py` for model/parameter changes
- Modify chunking strategy in `rag/chunking.py`
- Adjust retrieval settings for better results

---

## 💡 Pro Tips

1. **Better Memory**: Ask questions naturally - the system learns from conversations
2. **Clear Context**: Mention your project/domain explicitly for better responses
3. **Check Debug**: Watch the terminal output for 💾✅⏭️ emoji indicators
4. **Use Langfuse**: Add Langfuse keys to `.env` for detailed traces
5. **Restart Often**: After config changes, restart Streamlit

---

## 🆘 Need Help?

- 📖 Check [README.md](README.md) troubleshooting section
- 🐛 Open an issue on GitHub
- 💬 Review existing documentation
- 🔍 Search closed issues for solutions

---

## ⏱️ Summary Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Install Python dependencies |
| 2 | 1 min | Start Qdrant |
| 3 | 1 min | Configure .env |
| 4 | 30 sec | Initialize collections |
| 5 | 30 sec | Launch Streamlit |
| **Total** | **5 min** | **Ready to use!** |

---

**Welcome to Lumiere! 🌟 Happy querying!**
