# Lumiere Capstone Defense - Demo Script

**Version:** 1.0.0  
**Date:** December 23, 2025  
**Total Duration:** ~12 minutes  
**Presenter:** [Your Name]  
**Deployment URL:** https://lumiereworkspace.streamlit.app/

---

## 🎯 Demo Objectives

By the end of this demonstration, the audience will understand:
1. ✅ Lumiere's unique hybrid architecture (RAG + SQL + LLM)
2. ✅ The 9-node LangGraph workflow and decision logic
3. ✅ User isolation and multi-tenancy architecture
4. ✅ Dual-memory system (session + semantic)
5. ✅ Three operational modes and their use cases
6. ✅ Production-grade observability with LangSmith

---

## 📋 Pre-Demo Checklist

**Before Starting:**
- [ ] Open deployment URL: https://lumiereworkspace.streamlit.app/
- [ ] Clear browser cache/cookies for fresh session
- [ ] Have LangSmith dashboard open in another tab: https://smith.langchain.com
- [ ] Prepare sample documents (see SAMPLE_QUESTIONS.md)
- [ ] Test internet connection
- [ ] Close unnecessary browser tabs
- [ ] Set browser zoom to 100%

**Backup Plan:**
- [ ] Have screenshots ready if demo fails
- [ ] Local instance running as backup: `streamlit run app.py`
- [ ] Architecture diagram (lumiere_graph.png) accessible

---

## 🎬 PART 1: Introduction (30 seconds)

### What to Say:

> "Good [morning/afternoon], everyone. Today I'll be demonstrating **Lumiere**, an AI-powered knowledge workspace that combines three powerful capabilities: document understanding through RAG, data analysis through SQL, and general reasoning through LLMs.
>
> What makes Lumiere unique is its **intelligent routing system** that automatically determines which approach—or combination of approaches—is best for each user query. Let me show you how it works."

### What to Do:
1. Display the Lumiere homepage
2. Point to the three mode buttons at the top
3. Briefly hover over the architecture diagram if visible

### Timing Check: ⏱️ 0:30

---

## 🎬 PART 2: Architecture Overview (90 seconds)

### What to Say:

> "Let me briefly explain the architecture before we dive into the demo.
>
> Lumiere is built on **LangGraph**, a state machine framework from LangChain. The system uses a **9-node directed graph** where each node represents a specialized agent:
>
> 1. **Intent Node** - Classifies whether the query needs documents (RAG), data analysis (SQL), general knowledge, or a combination
> 2. **Retrieval Node** - Fetches relevant documents from Qdrant vector database
> 3. **Reasoning Node** - Generates answers using retrieved context
> 4. **General Reasoning Node** - Handles queries from general knowledge
> 5. **SQL Execution Node** - Generates and runs SQL queries on user data
> 6. **SQL Reasoning Node** - Interprets SQL results
> 7. **Visualization Node** - Creates interactive Plotly charts
> 8. **Critic Node** - Evaluates answer quality and decides: ACCEPT, REJECT, or RETRY
> 9. **Memory Write Node** - Stores successful interactions for future context
>
> The system supports **three modes**: All-In mode for hybrid queries, Chat with RAG for document Q&A, and Data Analyst for SQL analysis.
>
> Everything is **user-isolated**—each user gets their own vector collections, database, and memory storage. And all interactions are automatically traced through **LangSmith** for observability."

### What to Do:
1. Show the architecture diagram (lumiere_graph.png) if available
2. Briefly point to each mode button in the UI
3. Optional: Show the LangSmith dashboard

### Key Points to Emphasize:
- ✅ 9-node graph architecture
- ✅ Intelligent routing (intent classification)
- ✅ Critic node for quality control
- ✅ User isolation
- ✅ LangSmith observability

### Timing Check: ⏱️ 2:00

---

## 🎬 PART 3: Feature Demo - All-In Mode (3 minutes)

### Setup:
- Select "All-In Mode" 
- Have a sample document ready to upload (PDF about AI/ML recommended)

### What to Say:

> "Let's start with **All-In Mode**, which is the most powerful mode. This allows Lumiere to intelligently combine document knowledge, data analysis, and general reasoning.
>
> First, I'll upload a document to demonstrate the RAG capabilities."

### Demo Step 1: Document Upload (45 seconds)

**What to Do:**
1. Click "Upload Documents" in sidebar
2. Upload a sample PDF (e.g., "Introduction to Machine Learning")
3. Wait for processing to complete
4. Show the success message

**What to Say:**
> "When I upload a document, Lumiere:
> 1. Extracts the text
> 2. Splits it into semantic chunks using RecursiveCharacterTextSplitter
> 3. Generates embeddings using OpenAI's text-embedding-3-small model
> 4. Stores them in my user-specific Qdrant collection
> 
> Notice the collection name includes my user ID—this ensures complete data isolation."

### Demo Step 2: RAG Query (60 seconds)

**Sample Question:**
```
"What are the main types of machine learning mentioned in the document?"
```

**What to Do:**
1. Type the question in the chat input
2. Click Send
3. Wait for response (show the thinking process)
4. Point out the retrieved documents shown below the answer

**What to Say:**
> "Watch what happens behind the scenes:
> 1. The **Intent Node** classifies this as a RAG query
> 2. The **Retrieval Node** searches my vector database using semantic similarity
> 3. It retrieves the top 5 most relevant chunks and reranks them using CrossEncoder
> 4. The **Reasoning Node** generates an answer using ONLY the retrieved context
> 5. The **Critic Node** evaluates the answer quality
> 6. If accepted, the **Memory Write Node** stores this interaction
>
> Notice at the bottom—it shows which document chunks were used, with source citations. This provides transparency and allows users to verify the answer."

### Demo Step 3: Hybrid Query (75 seconds)

**Sample Question:**
```
"Based on the document, explain supervised learning and then show me the sales data for customers who made purchases over $1000"
```

**What to Do:**
1. Type the hybrid question
2. Wait for response
3. Point out both the explanation AND the data table
4. Highlight the SQL query that was generated

**What to Say:**
> "This is where Lumiere shines—handling **hybrid queries**. Notice this question has two parts:
> 1. A conceptual question about the document
> 2. A data analysis request
>
> The **Intent Node** detected BOTH needs and routed through:
> - First, the **Retrieval + Reasoning** path for the document explanation
> - Then, the **SQL Execution** path to query the database
> 
> The system automatically generated this SQL query, executed it, and presented the results. If I had asked for a visualization, it would have created an interactive Plotly chart as well.
>
> This is the power of All-In Mode—seamlessly combining multiple knowledge sources in a single response."

### Timing Check: ⏱️ 5:00

---

## 🎬 PART 4: Feature Demo - Chat with RAG (2 minutes)

### Setup:
- Switch to "Chat with RAG" mode using the mode selector

### What to Say:

> "Let me switch to **Chat with RAG** mode. This mode is optimized for document-focused Q&A, similar to ChatGPT with your documents. It's faster because it doesn't consider SQL or general knowledge—it's laser-focused on your uploaded content."

### Demo Step 1: Follow-up Question (60 seconds)

**Sample Question:**
```
"Can you explain that in simpler terms?"
```

**What to Do:**
1. Type the follow-up question
2. Wait for response
3. Show the conversation history in memory

**What to Say:**
> "Notice I didn't specify WHAT to simplify—I just said 'that.' This demonstrates Lumiere's **context awareness** through its dual-memory system:
>
> 1. **Session Memory** - Stores the last 5 conversation exchanges in-memory
> 2. **Semantic Memory** - Stores all successful interactions in Qdrant for long-term retrieval
>
> The agent reads the conversation history, identifies that 'that' refers to 'supervised learning' from my previous question, and provides a simpler explanation using the same document context.
>
> This context-awareness makes multi-turn conversations feel natural, not robotic."

### Demo Step 2: Document-Specific Query (60 seconds)

**Sample Question:**
```
"What page discusses neural networks?"
```

**What to Do:**
1. Type the question
2. Point out the source citations
3. Show the document chunk reference [doc_id:chunk_index]

**What to Say:**
> "In RAG mode, Lumiere maintains full traceability. Every answer includes source citations showing:
> - Which document was used
> - Which chunk (page section) contained the information
> - The relevance score from the retrieval
>
> This is critical for enterprise use cases where you need to verify information or comply with regulations. Users can always trace back to the source."

### Timing Check: ⏱️ 7:00

---

## 🎬 PART 5: Feature Demo - Data Analyst Mode (2.5 minutes)

### Setup:
- Switch to "Data Analyst" mode
- The pre-loaded database contains cars, customers, and sales tables

### What to Say:

> "Now let's switch to **Data Analyst** mode, which transforms Lumiere into an AI data analyst. This mode is perfect for business users who need insights from data but don't know SQL."

### Demo Step 1: Simple SQL Query (60 seconds)

**Sample Question:**
```
"Show me the top 5 customers by total sales"
```

**What to Do:**
1. Type the question
2. Wait for the SQL generation and execution
3. Point out the generated SQL query displayed
4. Show the results table

**What to Say:**
> "Behind the scenes:
> 1. The system inspects the database schema (cars, customers, sales tables)
> 2. Generates an appropriate SQL query using GPT-4o-mini
> 3. Executes it against the user's SQLite database
> 4. Presents results in a clean table format
>
> Notice it shows the SQL query that was executed—this provides transparency and helps users learn SQL by example."

### Demo Step 2: Visualization Query (90 seconds)

**Sample Question:**
```
"Create a bar chart showing total sales by car model"
```

**What to Do:**
1. Type the visualization request
2. Wait for the chart to render
3. Interact with the Plotly chart (hover, zoom)
4. Point out the chart is interactive

**What to Say:**
> "For visualization requests, Lumiere:
> 1. Generates the SQL query to fetch the data
> 2. Determines the best chart type (bar chart in this case)
> 3. Configures Plotly visualization settings
> 4. Creates an **interactive** chart
>
> Users can hover for details, zoom in, download the chart as PNG, and more. The visualization adapts to the data type automatically—time series get line charts, categorical comparisons get bar charts, distributions get histograms, etc.
>
> This workflow—from natural language question to interactive visualization—takes seconds and requires zero technical knowledge from the user."

### Timing Check: ⏱️ 9:30

---

## 🎬 PART 6: Observability with LangSmith (90 seconds)

### Setup:
- Switch to LangSmith dashboard tab
- Navigate to your Lumiere project

### What to Say:

> "One of the most important aspects of production AI systems is **observability**—the ability to monitor, debug, and improve the system. Lumiere uses **LangSmith** for automatic tracing.
>
> Let me show you what's happening under the hood."

### What to Do:
1. Show the LangSmith traces list
2. Click on the most recent trace
3. Expand the trace to show the node execution sequence
4. Point out timing information
5. Show input/output for each node

### What to Say:

> "Every single interaction with Lumiere is automatically traced. This gives us:
>
> 1. **Execution Flow** - See exactly which nodes were triggered and in what order
> 2. **Timing Information** - Identify performance bottlenecks (e.g., 'retrieval took 2.3 seconds')
> 3. **Input/Output Logging** - Debug issues by seeing exactly what data each node received and produced
> 4. **Error Tracking** - When something fails, we see exactly where and why
> 5. **Token Usage** - Monitor OpenAI API costs per interaction
>
> This is critical for:
> - Debugging production issues
> - Optimizing performance
> - Understanding user behavior
> - Cost management
> - Compliance and auditing
>
> And the best part—it requires ZERO manual instrumentation. Just set `LANGCHAIN_TRACING_V2=true` and LangSmith automatically captures everything."

### Timing Check: ⏱️ 11:00

---

## 🎬 PART 7: Critic Node & Quality Control (60 seconds)

### What to Say:

> "Before I wrap up, I want to highlight one of Lumiere's most important features: the **Critic Node**.
>
> Not all AI responses are good. Lumiere has a built-in quality control mechanism where every answer is evaluated before being shown to the user."

### What to Do:
1. Go back to the chat interface
2. Optionally trigger a retry scenario (if you have one prepared)

### What to Say:

> "The Critic Node evaluates each answer based on:
> 1. **Relevance** - Does it actually answer the question?
> 2. **Accuracy** - Is it supported by the retrieved context or data?
> 3. **Completeness** - Does it address all parts of the query?
> 4. **Clarity** - Is it well-structured and understandable?
>
> It can make three decisions:
> - **ACCEPT** - Good answer, show to user and store in memory
> - **REJECT** - Bad answer, show error to user
> - **RETRY** - Fixable issue, regenerate with improved context (max 2 retries)
>
> This self-evaluation mechanism significantly improves answer quality and catches hallucinations before they reach users. It's like having a second AI that checks the first AI's work."

### Timing Check: ⏱️ 12:00

---

## 🎬 PART 8: Conclusion (30 seconds)

### What to Say:

> "To summarize, Lumiere demonstrates several advanced concepts:
>
> 1. ✅ **Hybrid Architecture** - RAG + SQL + LLM in one system
> 2. ✅ **Intelligent Routing** - Automatic intent classification and node selection
> 3. ✅ **Quality Control** - Built-in critic for self-evaluation
> 4. ✅ **Context Awareness** - Dual-memory system for natural conversations
> 5. ✅ **User Isolation** - Multi-tenant architecture for data privacy
> 6. ✅ **Production-Grade Observability** - Full tracing with LangSmith
> 7. ✅ **Frozen Architecture** - Stable v1.0.0 with clear versioning policy
>
> The system is deployed on Streamlit Cloud, fully documented, and ready for production use.
>
> I'm happy to answer any questions about the architecture, implementation decisions, or technical deep-dives."

### What to Do:
1. Return to the homepage or show the architecture diagram
2. Prepare for Q&A

### Timing Check: ⏱️ 12:30

---

## 📊 Demo Summary Table

| Section | Duration | Key Points |
|---------|----------|------------|
| Introduction | 0:30 | Project overview, uniqueness |
| Architecture | 1:30 | 9-node graph, user isolation |
| All-In Mode | 3:00 | RAG upload, hybrid query, intelligent routing |
| Chat with RAG | 2:00 | Context awareness, follow-ups, source citations |
| Data Analyst | 2:30 | SQL generation, visualizations, interactivity |
| Observability | 1:30 | LangSmith tracing, debugging, monitoring |
| Critic Node | 1:00 | Quality control, retry mechanism |
| Conclusion | 0:30 | Summary, Q&A transition |
| **TOTAL** | **12:30** | **Complete walkthrough** |

---

## 🎯 Key Messages to Emphasize

Throughout the demo, repeatedly emphasize these differentiators:

1. **Hybrid Intelligence**
   - "Unlike traditional RAG systems that only work with documents, Lumiere combines three knowledge sources..."

2. **Intelligent Routing**
   - "The system automatically determines the best approach for each query..."

3. **Quality Control**
   - "Built-in self-evaluation through the Critic Node ensures high-quality responses..."

4. **Context Awareness**
   - "Dual-memory system enables natural, multi-turn conversations..."

5. **Production-Ready**
   - "Full observability, user isolation, frozen architecture—this is production-grade..."

6. **User-Centric Design**
   - "No technical knowledge required—just ask questions in natural language..."

---

## 🚨 Common Issues & Recovery

### Issue 1: Slow Response Time
**If the demo is slow:**
- "As you can see, the system is processing multiple complex operations—retrieval, LLM inference, and quality evaluation. In production, we'd optimize with caching and parallel processing."

### Issue 2: Wrong Answer
**If the AI gives a poor answer:**
- "Perfect example of why we need the Critic Node! In a real scenario, this might trigger a RETRY. Let me show you the LangSmith trace to see what happened..."

### Issue 3: Upload Fails
**If document upload fails:**
- "This is why we have comprehensive error handling. The system will show a user-friendly error message. Let me show you using a different document..."
- **Backup:** Use screenshots or switch to local instance

### Issue 4: Network Issues
**If deployment is down:**
- "Let me switch to the local instance I have running as backup..."
- **Backup:** Run local streamlit app
- **Last Resort:** Use screenshots and walk through them

### Issue 5: Questions During Demo
**If interrupted with questions:**
- "Great question! Let me finish this demo section, and I'll address that in detail during Q&A."
- **Alternative:** "Let me show you that right now..." (if it fits naturally)

---

## 💡 Tips for Successful Demo

### Before Demo:
1. ✅ Practice the demo 3-5 times to get timing right
2. ✅ Prepare backup answers for common questions
3. ✅ Test the deployment the morning of your defense
4. ✅ Have screenshots ready as backup
5. ✅ Clear browser data for a fresh session
6. ✅ Close unnecessary applications

### During Demo:
1. ✅ Speak clearly and at a moderate pace
2. ✅ Make eye contact with the panel (not just the screen)
3. ✅ Explain WHAT you're doing before clicking
4. ✅ Point to important elements on screen
5. ✅ Pause after key points to let them sink in
6. ✅ Show confidence—you built this!

### After Demo:
1. ✅ Transition smoothly to Q&A
2. ✅ Have the architecture diagram ready
3. ✅ Be ready to dive deeper into any component
4. ✅ Admit if you don't know something, then explain how you'd find out

---

## 📝 Narrator Notes

### Pacing:
- **Slow down** when explaining complex concepts (architecture, critic node)
- **Speed up** during routine actions (clicking, waiting for responses)
- **Pause** after asking rhetorical questions or making key points

### Tone:
- **Confident** - You built this, you understand it deeply
- **Enthusiastic** - Show passion for your work
- **Professional** - This is production-grade software

### Body Language:
- Use hand gestures to emphasize points
- Point to screen elements you're discussing
- Maintain good posture
- Smile—enthusiasm is contagious!

---

## 🎓 Capstone Defense Context

### Why This Demo Works:

1. **Shows Technical Depth**
   - 9-node LangGraph architecture
   - Vector databases (Qdrant)
   - State management
   - Observability patterns

2. **Demonstrates System Thinking**
   - User isolation for multi-tenancy
   - Quality control mechanisms
   - Error handling
   - Production deployment

3. **Proves Practical Value**
   - Real-world use cases
   - Interactive visualizations
   - Natural language interface
   - Context-aware conversations

4. **Exhibits Professional Maturity**
   - Comprehensive documentation
   - Architecture freeze
   - Semantic versioning
   - Observability and monitoring

---

## 📚 Related Documents

- [SAMPLE_QUESTIONS.md](./SAMPLE_QUESTIONS.md) - Pre-tested questions for demo
- [QA_PREP.md](./QA_PREP.md) - Anticipated questions and answers
- [../docs/GRAPH_ARCHITECTURE.md](../docs/GRAPH_ARCHITECTURE.md) - Technical deep-dive
- [../docs/ARCHITECTURE_FREEZE.md](../docs/ARCHITECTURE_FREEZE.md) - Frozen components

---

**Good luck with your capstone defense! You've built something impressive—now go show it off! 🚀**
