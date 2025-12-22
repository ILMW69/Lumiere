# Changelog

All notable changes to Lumiere will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README.md with full project documentation
- CONTRIBUTING.md with contribution guidelines
- QUICKSTART.md for rapid setup
- CHANGELOG.md for tracking changes

## [0.2.0] - 2025-12-22

### Added
- **Semantic Memory System** 🧠
  - Long-term memory storage in Qdrant vector database
  - Automatic conversation embedding and storage
  - Context-aware responses using past interactions
  - Memory retrieval in intent agent
  - Memory statistics dashboard in UI
  - Quality filtering via critic agent (only ACCEPT decisions stored)
  
- **Memory Management Tools**
  - `memory/semantic_memory.py`: Core memory operations
  - `scripts/init_semantic_memory.py`: Initialization script
  - Memory viewer in Streamlit sidebar
  - Search functionality for stored memories
  
- **Documentation**
  - `SEMANTIC_MEMORY.md`: Complete memory system guide
  - `SEMANTIC_MEMORY_FIX.md`: Bug fix documentation
  - `GRAPH_ARCHITECTURE.md`: Detailed workflow documentation
  - Updated graph visualization with memory integration
  - `graph_visualization.png`: Visual architecture diagram

### Changed
- **Graph Routing**: Critic always routes to memory_write node
- **Memory Write Node**: Now stores on ALL ACCEPT decisions (not just with memory_signal)
- **State Management**: Fixed field names (query→question, mode→reasoning_mode)
- **Intent Agent**: Retrieves top 3 relevant memories before classification
- **Database**: Clarified SQLite for data, Qdrant for vectors (removed PostgreSQL confusion)

### Fixed
- Qdrant user_id filtering moved from query-time to post-retrieval (no index required)
- Embedding function changed from get_embeddings() to embed_text()
- Qdrant API compatibility (added fallback for search() vs query_points())
- Memory write node condition logic (removed memory_signal requirement)
- Query and mode fields now correctly retrieved from state

### Technical Details
- Semantic memory uses OpenAI text-embedding-3-small (1536 dimensions)
- Memories stored in 'agent_memories' collection
- Metadata includes: mode, agents_used, retry_count, session_id, user_id
- Data analyst mode includes additional metadata: SQL query, chart_type
- Retrieval threshold: 0.75 similarity score
- Top-k retrieval: 3 memories per query

## [0.1.0] - 2025-12-15

### Added
- **Multi-Agent RAG System**
  - Intent classification agent
  - RAG retrieval and reasoning agents
  - SQL execution and reasoning agents
  - Critic agent for quality validation
  - Visualization agent for data analyst mode

- **Core Features**
  - LangGraph-based workflow orchestration
  - Qdrant vector database integration
  - OpenAI LLM and embeddings
  - Streamlit UI
  - Document ingestion pipeline
  - Hybrid chunking strategy
  - Session memory management

- **Data Analyst Mode**
  - Natural language to SQL conversion
  - Automated chart generation (bar, line, pie, scatter)
  - Interactive Plotly visualizations
  - SQLite database backend

- **Observability**
  - Langfuse integration
  - Token usage tracking
  - Performance metrics
  - Debug logging with emoji indicators

- **Configuration**
  - Environment-based settings
  - Configurable model parameters
  - Retrieval customization
  - Chunking options

### Initial Release Features
- RAG mode for document Q&A
- SQL mode for data analysis
- General chat mode
- Multi-modal support (all_in, chat_rag, data_analyst)
- Document support (PDF, TXT, MD)
- Batch ingestion
- Source attribution
- Retry mechanism (max 1 retry)
- Conversation history tracking

---

## Version History

- **v0.2.0** (Dec 22, 2025): Semantic Memory Integration
- **v0.1.0** (Dec 15, 2025): Initial Release

---

## Upgrade Guide

### From v0.1.0 to v0.2.0

**New Dependencies:**
No new packages required - semantic memory uses existing Qdrant infrastructure.

**Breaking Changes:**
None - all changes are backwards compatible.

**Migration Steps:**

1. **Initialize semantic memory collection**
   ```bash
   python -c "from memory.semantic_memory import create_memory_collection; create_memory_collection()"
   ```

2. **Optional: Seed initial memories**
   ```bash
   python scripts/init_semantic_memory.py
   ```

3. **Restart application**
   ```bash
   streamlit run app.py
   ```

4. **Verify memory system**
   - Check sidebar for "🧠 Semantic Memory" section
   - Ask a few questions
   - Verify memory count increases

**New Features Available:**
- Automatic conversation storage
- Context-aware responses
- Memory search in UI
- Memory statistics tracking

**Configuration Changes:**
Optional - add to `.env`:
```env
MEMORY_TOP_K=3
MEMORY_MIN_SCORE=0.75
```

---

## Future Roadmap

See [README.md](README.md) for detailed roadmap.

### v0.3.0 (Planned)
- Multi-user support with isolation
- Memory pruning and consolidation
- Advanced query routing
- REST API endpoints

### v0.4.0 (Planned)
- Custom embedding models
- Memory analytics dashboard
- Feedback loop for refinement
- Advanced visualization types

### v1.0.0 (Future)
- Production-ready deployment
- Comprehensive test coverage
- Performance optimizations
- Plugin system
- Enterprise features

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on contributing to Lumiere.

---

## Release Process

1. Update CHANGELOG.md with changes
2. Bump version in relevant files
3. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release with notes

---

**For questions or issues, please open a GitHub issue.**
