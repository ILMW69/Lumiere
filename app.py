import streamlit as st
import os

# Load Streamlit secrets into environment variables BEFORE any other imports
if hasattr(st, 'secrets'):
    for key in ['OPENAI_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_BASE_URL']:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

import uuid
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from graph.rag_graph import build_graph
from memory.session_memory import get_session_memory, append_session_memory
from langfuse import observe

st.set_page_config(
    page_title="Lumiere",
    layout="wide",
    page_icon="🌟",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Apple-like Custom CSS
# ---------------------------
st.markdown("""
<style>
    /* Apple-inspired color palette and typography */
    :root {
        --apple-blue: #007AFF;
        --apple-green: #34C759;
        --apple-gray: #86868B;
        --apple-dark: #1D1D1F;
        --apple-bg: #F5F5F7;
    }
    
    /* Main container styling */
    .main {
        background-color: var(--apple-bg);
    }
    
    /* Header styling */
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 600;
        color: var(--apple-dark);
        letter-spacing: -0.5px;
    }
    
    /* Subtitle styling */
    .subtitle {
        color: var(--apple-gray);
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: -1rem;
        margin-bottom: 2rem;
    }
    
    /* Feature badges */
    .feature-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        background: linear-gradient(135deg, var(--apple-blue) 0%, #0051D5 100%);
        color: white;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
    }
    
    /* Cards with shadow */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA;
        border-right: 1px solid #E5E5E7;
    }
    
    /* Sidebar text visibility */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--apple-dark) !important;
    }
    
    /* Sidebar metrics */
    section[data-testid="stSidebar"] [data-testid="stMetric"] {
        background: white;
        color: var(--apple-dark);
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: var(--apple-gray) !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--apple-dark) !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Metrics styling */
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* Clean expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat input styling */
    .stChatInput {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Initialize Sample Data (First Run)
# ---------------------------
@st.cache_resource
def initialize_app():
    """Initialize app resources on first run."""
    try:
        from rag.qdrant_client import client
        from rag.collections import ensure_collection_exists
        from config.settings import DOCUMENT_COLLECTION_NAME
        
        # Ensure collections exist
        ensure_collection_exists(DOCUMENT_COLLECTION_NAME)
        
        # Check if we need sample data
        collection_info = client.get_collection(DOCUMENT_COLLECTION_NAME)
        if collection_info.points_count == 0:
            print("📚 No documents found. Initializing sample data...")
            from scripts.init_sample_data import initialize_sample_data
            initialize_sample_data()
            return "Sample data initialized"
        else:
            return f"Ready ({collection_info.points_count} documents)"
    except Exception as e:
        print(f"⚠️ Initialization warning: {e}")
        return "Ready"

# Initialize on first load
init_status = initialize_app()

# ---------------------------
# Helper Functions
# ---------------------------
def render_chart(viz_config):
    """Render visualization based on config from visualization agent."""
    if not viz_config:
        return
    
    chart_type = viz_config.get("chart_type")
    data = viz_config.get("data", [])
    columns = viz_config.get("columns", [])
    title = viz_config.get("title", "Data Visualization")
    x_col = viz_config.get("x_column")
    y_col = viz_config.get("y_column")
    reasoning = viz_config.get("reasoning", "")
    
    if not data or not columns:
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    st.divider()
    st.subheader(f"📊 {title}")
    if reasoning:
        st.caption(reasoning)
    
    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig, width='stretch')
            
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
            st.plotly_chart(fig, width='stretch')
            
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=title)
            st.plotly_chart(fig, width='stretch')
            
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=title)
            st.plotly_chart(fig, width='stretch')
            
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, title=title)
            st.plotly_chart(fig, width='stretch')
        
        # Show data table below chart
        with st.expander("📋 View Data Table"):
            st.dataframe(df, width='stretch')
            
            # Add download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
    
    except Exception as e:
        st.error(f"Error rendering chart: {e}")
        # Fallback to table
        st.dataframe(df, use_container_width=True)

# ---------------------------
# Modern Header
# ---------------------------
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Lumiere")
    st.markdown('<p class="subtitle">Intelligent Knowledge Assistant with RAG & Analytics</p>', unsafe_allow_html=True)

with col2:
    st.markdown("###")  # Spacing
    if init_status:
        st.caption(f"✓ {init_status}")

# Feature badges
st.markdown("""
<div style="margin: -1rem 0 1.5rem 0;">
    <span class="feature-badge">RAG-Powered</span>
    <span class="feature-badge">Data Analytics</span>
    <span class="feature-badge">Semantic Memory</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------
# Session initialization
# ---------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = "streamlit_user"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "lumiere_mode" not in st.session_state:
    st.session_state.lumiere_mode = "all_in"  # Default mode

# ---------------------------
# Clean Sidebar
# ---------------------------
with st.sidebar:
    # Settings Section
    st.markdown("### Settings")
    
    # Mode selector (compact)
    mode_options = {
        "all_in": "All Features",
        "chat_rag": "Chat + Documents",
        "data_analyst": "Analytics"
    }
    
    selected_mode = st.selectbox(
        "Mode",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        index=list(mode_options.keys()).index(st.session_state.lumiere_mode),
        label_visibility="collapsed"
    )
    
    if selected_mode != st.session_state.lumiere_mode:
        st.session_state.lumiere_mode = selected_mode
        st.rerun()
    
    # Workflow toggle
    show_streaming = st.checkbox("Show Workflow", value=True)
    
    # Clear button
    if st.button("Clear Session", use_container_width=True, type="secondary"):
        from memory.session_memory import clear_session_memory
        clear_session_memory(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.turn_count = 0
        st.rerun()
    
    st.divider()
    
    # Document Library
    st.markdown("### Document Library")
    
    try:
        from rag.qdrant_client import client
        from config.settings import DOCUMENT_COLLECTION_NAME
        
        # Scroll all documents with their metadata
        docs = client.scroll(
            collection_name=DOCUMENT_COLLECTION_NAME,
            limit=100,  # Adjust if you have more documents
            with_payload=True,
            with_vectors=False
        )[0]
        
        if docs:
            # Group documents by their source (which contains the title)
            doc_info = {}
            for doc in docs:
                if doc.payload:
                    # Try to get title from different fields
                    source = doc.payload.get("source", "Unknown")
                    
                    # Extract clean title from source (remove " (Sample Document)" suffix)
                    if " (Sample Document)" in source:
                        title = source.replace(" (Sample Document)", "")
                    elif source != "Unknown":
                        title = source
                    else:
                        title = doc.payload.get("title", "Untitled")
                    
                    # Group by title, store chunk count
                    if title not in doc_info:
                        doc_info[title] = {
                            "chunks": 0
                        }
                    doc_info[title]["chunks"] += 1
            
            # Display documents in a clean list
            for idx, (title, info) in enumerate(doc_info.items(), 1):
                with st.container():
                    st.markdown(f"**{idx}. {title}**")
                    st.caption(f"{info['chunks']} chunks")
                    if idx < len(doc_info):
                        st.markdown("")  # Small spacing
        else:
            st.info("No documents stored yet")
            
    except Exception as e:
        st.warning(f"Unable to load documents: {str(e)}")
    
    st.divider()
    
    # Advanced Section (collapsed by default)
    with st.expander("Advanced", expanded=False):
        # Memory search
        st.caption("**Search Memories**")
        try:
            from memory.semantic_memory import retrieve_memories
            
            search_query = st.text_input("Search:", placeholder="e.g., RAG systems", key="memory_search", label_visibility="collapsed")
            if search_query:
                memories = retrieve_memories(
                    query=search_query,
                    top_k=3,
                    user_id=st.session_state.user_id,
                    min_score=0.6
                )
                
                if memories:
                    for i, mem in enumerate(memories, 1):
                        st.caption(f"**{i}.** {mem['content'][:100]}...")
                        st.caption(f"Score: {mem['score']:.2f} | {mem['timestamp'][:10]}")
                        if i < len(memories):
                            st.markdown("---")
                else:
                    st.info("No memories found")
        except Exception as e:
            st.warning("Memory search unavailable")
        
        st.markdown("---")
        
        # Quick upload
        st.caption("**Quick Upload**")
        upload_type = st.radio("Type:", ["PDF", "CSV"], horizontal=True, label_visibility="collapsed")
        
        if upload_type == "PDF":
            quick_file = st.file_uploader("Upload", type=['pdf'], key="quick_pdf", label_visibility="collapsed")
            if quick_file and st.button("Store", key="store_pdf"):
                from rag.pdf_processor import process_and_store_pdf
                with st.spinner("Processing..."):
                    result = process_and_store_pdf(quick_file, quick_file.name, st.session_state.user_id)
                    if result["success"]:
                        st.success(f"✓ {result['chunks_stored']} chunks")
                    else:
                        st.error(result["error"])
        else:
            quick_file = st.file_uploader("Upload", type=['csv'], key="quick_csv", label_visibility="collapsed")
            if quick_file and st.button("Store", key="store_csv"):
                from database.csv_processor import process_and_store_csv
                with st.spinner("Processing..."):
                    result = process_and_store_csv(quick_file, quick_file.name, user_id=st.session_state.user_id)
                    if result["success"]:
                        st.success(f"✓ {result['rows']} rows")
                    else:
                        st.error(result["error"])
        
        st.caption("💡 Visit Documents page for more options")

# ---------------------------
# Display chat history
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Chat input
# ---------------------------
user_input = st.chat_input("Ask Lumiere something...")

if user_input:
    # Add user message to UI
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Build initial graph state
    previous_memory = get_session_memory(st.session_state.session_id)
    conversation_context = [m for m in previous_memory if m["type"] == "conversation"]
    
    initial_state = {
        "messages": [user_input],
        "session_id": st.session_state.session_id,
        "user_id": st.session_state.user_id,
        "lumiere_mode": st.session_state.lumiere_mode,  # Pass mode to graph
        "intent": None,
        "needs_rag": None,
        "retrieved_docs": None,
        "answer": None,
        "retry_count": 0,
        "decision": None,
        "reasoning_mode": None,
    }

    # Create containers for streaming display
    with st.chat_message("assistant"):
        # Workflow visualization container (conditional)
        if show_streaming:
            workflow_container = st.expander("🔄 Workflow Execution", expanded=True)
        
        # Answer container (will be populated at the end)
        answer_container = st.empty()
        
        if show_streaming:
            with workflow_container:
                # Create placeholders for each node execution
                stream_output = st.empty()
        
        # Node icons and descriptions
        node_info = {
            "intent": {"icon": "🎯", "name": "Intent Agent", "desc": "Classifying user query"},
            "retrieve": {"icon": "🔍", "name": "Retrieval Agent", "desc": "Searching documents"},
            "reason": {"icon": "🧠", "name": "Reasoning Agent", "desc": "Grounded reasoning with context"},
            "general_reason": {"icon": "💭", "name": "General Agent", "desc": "General knowledge reasoning"},
            "sql_execute": {"icon": "🗄️", "name": "SQL Agent", "desc": "Executing database query"},
            "sql_reason": {"icon": "📝", "name": "SQL Reasoning", "desc": "Interpreting query results"},
            "visualize": {"icon": "📊", "name": "Visualization Agent", "desc": "Generating charts and graphs"},
            "critic": {"icon": "🔎", "name": "Critic Agent", "desc": "Validating answer quality"},
            "memory_write": {"icon": "💾", "name": "Memory Agent", "desc": "Storing conversation"},
        }
        
        @observe(name="streamlit_streaming_interaction", as_type="generation")
        def run_streaming_chat(state, session_id, user_id, user_query, turn):
            """Stream the graph execution with real-time updates"""
            from opentelemetry import trace
            
            # Set trace attributes
            span = trace.get_current_span()
            if span:
                span.set_attribute("session_id", session_id)
                span.set_attribute("user_id", user_id)
                span.set_attribute("turn", turn)
                span.set_attribute("user_query", user_query)
                span.set_attribute("tags", "streamlit,streaming,chat")
            
            # Stream through the graph
            final_state = None
            nodes_executed = []
            execution_log = []
            
            try:
                for event in st.session_state.graph.stream(state):
                    # event is a dict like {"node_name": state_update}
                    for node_name, node_state in event.items():
                        nodes_executed.append(node_name)
                        
                        # Get node information
                        info = node_info.get(node_name, {"icon": "⚙️", "name": node_name.title(), "desc": "Processing"})
                        
                        # Build execution details
                        exec_details = {
                            "node": node_name,
                            "name": info["name"],
                            "icon": info["icon"],
                            "desc": info["desc"],
                            "input": {},
                            "output": {}
                        }
                        
                        # Capture relevant inputs
                        if node_name == "intent":
                            messages = node_state.get("messages") or [""]
                            exec_details["input"] = {"query": messages[0][:100] if messages else ""}
                            exec_details["output"] = {
                                "intent": node_state.get("intent"),
                                "needs_rag": node_state.get("needs_rag")
                            }
                        elif node_name == "retrieve":
                            messages = node_state.get("messages") or [""]
                            exec_details["input"] = {"query": messages[0][:100] if messages else ""}
                            docs = node_state.get("retrieved_docs") or []
                            exec_details["output"] = {
                                "documents_found": len(docs) if docs else 0,
                                "top_doc": docs[0].get("text", "")[:80] + "..." if docs else "None"
                            }
                        elif node_name in ["reason", "general_reason"]:
                            messages = node_state.get("messages") or [""]
                            retrieved_docs = node_state.get("retrieved_docs") or []
                            exec_details["input"] = {
                                "query": messages[0][:100] if messages else "",
                                "context_docs": len(retrieved_docs) if retrieved_docs else 0
                            }
                            answer = node_state.get("answer") or ""
                            exec_details["output"] = {
                                "reasoning_mode": node_state.get("reasoning_mode"),
                                "answer_preview": answer[:100] + "..." if answer else ""
                            }
                        elif node_name == "critic":
                            answer = node_state.get("answer") or ""
                            exec_details["input"] = {"answer_length": len(answer) if answer else 0}
                            exec_details["output"] = {
                                "decision": node_state.get("decision"),
                                "has_memory": bool(node_state.get("memory_signal"))
                            }
                        elif node_name == "memory_write":
                            mem_signal = node_state.get("memory_signal") or {}
                            exec_details["input"] = {"memory_type": mem_signal.get("type") if mem_signal else "None"}
                            exec_details["output"] = {"stored": True}
                        
                        execution_log.append(exec_details)
                        
                        # Update streaming display
                        if show_streaming:
                            with stream_output.container():
                                for i, exec_item in enumerate(execution_log):
                                    # Create compact display
                                    cols = st.columns([1, 3, 3])
                                    
                                    with cols[0]:
                                        st.markdown(f"**{exec_item['icon']} {i+1}**")
                                    
                                    with cols[1]:
                                        st.markdown(f"<small><strong>{exec_item['name']}</strong><br/><em>{exec_item['desc']}</em></small>", unsafe_allow_html=True)
                                    
                                    with cols[2]:
                                        # Show input/output in compact format
                                        if exec_item['input']:
                                            input_str = ", ".join([f"{k}: {v}" for k, v in exec_item['input'].items() if v])
                                            st.markdown(f"<small>📥 <code>{input_str[:80]}</code></small>", unsafe_allow_html=True)
                                        if exec_item['output']:
                                            output_str = ", ".join([f"{k}: {v}" for k, v in exec_item['output'].items() if v is not None])
                                            st.markdown(f"<small>📤 <code>{output_str[:80]}</code></small>", unsafe_allow_html=True)
                                    
                                    st.markdown("<hr style='margin: 5px 0; opacity: 0.3;'/>", unsafe_allow_html=True)
                        
                        final_state = node_state
                        time.sleep(0.2)  # Small delay for visual effect
                
                # Set final output attributes
                if span and final_state:
                    span.set_attribute("answer", final_state.get("answer", ""))
                    span.set_attribute("intent", final_state.get("intent", ""))
                    span.set_attribute("needs_rag", str(final_state.get("needs_rag", False)))
                    span.set_attribute("reasoning_mode", final_state.get("reasoning_mode", ""))
                    span.set_attribute("nodes_executed", ",".join(nodes_executed))
                
                return final_state
                
            except Exception as e:
                # Show error in workflow
                if show_streaming:
                    stream_output.error(f"❌ Error during execution: {str(e)}")
                raise
        
        # Execute streaming workflow
        try:
            result = run_streaming_chat(
                initial_state,
                st.session_state.session_id,
                st.session_state.user_id,
                user_input,
                st.session_state.turn_count + 1
            )
            
            answer = result.get("answer", "Sorry, I couldn't generate an answer.")
            
            # Display the final answer
            answer_container.markdown(answer)
            
            # Display visualization if available (Data Analyst mode)
            viz_config = result.get("visualization_config")
            if viz_config and viz_config.get("chart_type") != "table":
                render_chart(viz_config)
            
        except Exception as e:
            error_msg = str(e)
            if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
                answer = "⏱️ Sorry, the request timed out. The vector database might be slow or unreachable. Please try again."
            else:
                answer = f"❌ An error occurred: {error_msg}"
            
            result = {
                "answer": answer,
                "intent": "error",
                "needs_rag": False,
                "reasoning_mode": "error"
            }
            
            answer_container.error(answer)
    
    # Increment turn count
    st.session_state.turn_count += 1

    # Store conversation in memory
    append_session_memory(
        session_id=st.session_state.session_id,
        item={
            "type": "conversation",
            "content": f"User: {user_input}",
            "turn": st.session_state.turn_count
        }
    )
    
    append_session_memory(
        session_id=st.session_state.session_id,
        item={
            "type": "conversation",
            "content": f"Assistant: {answer}",
            "turn": st.session_state.turn_count
        }
    )

    # Add assistant message to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
