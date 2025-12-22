# 📚 Lumiere Documentation Index

Welcome to Lumiere's documentation! This index will help you find the information you need.

## 🚀 Getting Started

Start here if you're new to Lumiere:

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡
   - 5-minute setup guide
   - Step-by-step installation
   - First steps after launch
   - Common issues and solutions

2. **[README.md](../README.md)** 📖
   - Project overview and vision
   - Complete feature list
   - Detailed installation guide
   - Usage examples
   - Configuration options
   - Troubleshooting

## 🏗️ Architecture & Design

Understand how Lumiere works:

3. **[GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md)** 🔄
   - Complete workflow documentation
   - Node-by-node descriptions
   - All workflow paths explained
   - External system integration
   - Configuration details
   - Future enhancements

4. **[graph_visualization.png](graph_visualization.png)** 📊
   - Visual system architecture
   - Color-coded components
   - Flow paths illustrated
   - External connections shown

5. **[graph_visualization.mmd](graph_visualization.mmd)** 🎨
   - Mermaid diagram source
   - Interactive visualization
   - View in Mermaid editor

## 🧠 Semantic Memory System

Learn about the memory system:

6. **[SEMANTIC_MEMORY.md](SEMANTIC_MEMORY.md)** 💾
   - Complete memory system guide
   - How it works
   - Memory types explained
   - Storage and retrieval
   - Use cases and examples
   - Configuration options
   - API reference

7. **[SEMANTIC_MEMORY_FIX.md](SEMANTIC_MEMORY_FIX.md)** 🔧
   - Bug fixes and solutions
   - Qdrant index error resolution
   - Embedding function fixes
   - API compatibility fixes

## 🤝 Contributing

Help improve Lumiere:

8. **[CONTRIBUTING.md](CONTRIBUTING.md)** 🌟
   - Contribution guidelines
   - Development setup
   - Code style guide
   - PR process
   - Bug reporting
   - Feature requests

9. **[CHANGELOG.md](CHANGELOG.md)** 📝
   - Version history
   - What's new in each release
   - Breaking changes
   - Upgrade guides
   - Future roadmap

## 📂 Additional Documentation

### Code Documentation

- **[agents/](agents/)** - Agent implementations
  - `intent_agent.py` - Intent classification + memory retrieval
  - `reasoning_agent.py` - RAG reasoning logic
  - `sql_agent.py` - SQL generation and execution
  - `critic_agent.py` - Quality validation
  - `viz_agent.py` - Visualization generation

- **[memory/](memory/)** - Memory system
  - `semantic_memory.py` - Core memory operations

- **[rag/](rag/)** - RAG components
  - `chunking.py` - Document chunking
  - `embeddings.py` - Embedding generation
  - `retriever.py` - Semantic search
  - `ingest.py` - Document ingestion

- **[graph/](graph/)** - Workflow orchestration
  - `rag_graph.py` - LangGraph workflow
  - `state.py` - State management

### Configuration Files

- **`.env.example`** - Environment variables template
- **`requirements.txt`** - Python dependencies
- **`config/settings.py`** - Application settings

## 🎯 Documentation by Use Case

### "I want to install Lumiere"
→ Start with **[QUICKSTART.md](QUICKSTART.md)**

### "I want to understand how it works"
→ Read **[GRAPH_ARCHITECTURE.md](GRAPH_ARCHITECTURE.md)**
→ View **[graph_visualization.png](graph_visualization.png)**

### "I want to learn about semantic memory"
→ Read **[SEMANTIC_MEMORY.md](SEMANTIC_MEMORY.md)**

### "I want to contribute"
→ Check **[CONTRIBUTING.md](CONTRIBUTING.md)**

### "I'm having issues"
→ See troubleshooting in **[README.md](README.md)** or **[QUICKSTART.md](QUICKSTART.md)**

### "I want to customize Lumiere"
→ Review configuration in **[README.md](README.md)** and `config/settings.py`

### "I want to see what's new"
→ Check **[CHANGELOG.md](CHANGELOG.md)**

## 📊 Documentation Statistics

| Document | Lines | Size | Purpose |
|----------|-------|------|---------|
| README.md | 625 | 17KB | Main documentation |
| CONTRIBUTING.md | 300 | 6.5KB | Contribution guide |
| QUICKSTART.md | 235 | 4.8KB | Quick setup |
| GRAPH_ARCHITECTURE.md | 461 | 12KB | Architecture details |
| SEMANTIC_MEMORY.md | 400+ | 15KB | Memory system |
| CHANGELOG.md | 250 | 5.6KB | Version history |
| graph_visualization.png | - | 80KB | Visual diagram |

**Total: ~2,300 lines of documentation** 📚

## 🔍 Search Tips

### Finding Specific Information

**Installation:**
- QUICKSTART.md: Steps 1-5
- README.md: "Installation" section

**Configuration:**
- README.md: "Configuration" section
- .env.example: All environment variables

**Troubleshooting:**
- README.md: "Troubleshooting" section
- QUICKSTART.md: "Common First-Time Issues"

**API Reference:**
- SEMANTIC_MEMORY.md: "API Reference" section
- Code files: Docstrings in source

**Examples:**
- README.md: "Usage Guide" section
- QUICKSTART.md: "First Steps After Launch"

## 🆘 Still Need Help?

1. **Search existing docs** using Ctrl+F in your browser
2. **Check closed GitHub issues** for similar problems
3. **Open a new issue** if you can't find answers
4. **Review code comments** in source files

## 📱 Mobile-Friendly

All documentation is:
- ✅ Markdown formatted
- ✅ Mobile-responsive
- ✅ GitHub-compatible
- ✅ Printable
- ✅ Copy-paste friendly

## 🔄 Keeping Documentation Updated

Documentation is kept up-to-date with each release:

1. **Code changes** → Update relevant docs
2. **New features** → Add to README + CHANGELOG
3. **Bug fixes** → Document in CHANGELOG
4. **Breaking changes** → Highlight in CHANGELOG + README

## 📅 Last Updated

This documentation index was last updated: **December 22, 2025**

Current version: **v0.2.0** (Semantic Memory Integration)

---

## 📖 Reading Order Recommendations

### For New Users (Recommended path):
1. QUICKSTART.md - Get it running
2. README.md (Quick Start section) - Learn basics
3. SEMANTIC_MEMORY.md (Overview) - Understand memory
4. GRAPH_ARCHITECTURE.md - Deep dive

### For Contributors:
1. README.md - Project overview
2. CONTRIBUTING.md - Guidelines
3. GRAPH_ARCHITECTURE.md - System design
4. CHANGELOG.md - Current state

### For Researchers/Students:
1. README.md - Full documentation
2. GRAPH_ARCHITECTURE.md - Technical details
3. SEMANTIC_MEMORY.md - Memory system
4. Source code - Implementation

---

**Happy reading! 📚 If you find any documentation gaps, please open an issue or PR!**
