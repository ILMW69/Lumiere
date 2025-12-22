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

st.set_page_config(page_title="Lumiere", layout="wide")

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

st.title("✨ Lumiere")
st.caption("Agentic RAG Knowledge Workspace")

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
# Sidebar: Session Info & Memory
# ---------------------------
with st.sidebar:
    st.header("Session Info")
    st.text(f"Session ID: {st.session_state.session_id[:8]}...")
    st.text(f"Turn: {st.session_state.turn_count}")
    
    st.divider()
    
    # Lumiere Mode Selection
    st.subheader("🎯 Lumiere Mode")
    
    mode_options = {
        "all_in": "🌟 All-in Mode",
        "chat_rag": "💬 Chat & Documents",
        "data_analyst": "📊 Data Analyst Mode"
    }
    
    mode_descriptions = {
        "all_in": "Full capabilities: Chat, Documents (RAG), and Data queries (SQL)",
        "chat_rag": "General chat and document search only (no database queries)",
        "data_analyst": "Data queries with automatic visualizations (charts, graphs, insights)"
    }
    
    selected_mode = st.radio(
        "Select Mode:",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        index=list(mode_options.keys()).index(st.session_state.lumiere_mode),
        help="Choose how Lumiere should respond to your queries"
    )
    
    # Update mode if changed
    if selected_mode != st.session_state.lumiere_mode:
        st.session_state.lumiere_mode = selected_mode
        st.rerun()
    
    # Show current mode description
    st.caption(f"ℹ️ {mode_descriptions[st.session_state.lumiere_mode]}")
    
    st.divider()
    
    # Streaming toggle
    st.subheader("⚙️ Settings")
    show_streaming = st.toggle("Show Workflow Streaming", value=True, help="Toggle to show/hide real-time workflow execution")
    
    if st.button("Clear Memory"):
        from memory.session_memory import clear_session_memory
        clear_session_memory(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.turn_count = 0
        st.success("Memory cleared!")
        st.rerun()
    
    st.divider()
    
    # 🧠 Semantic Memory Viewer
    st.subheader("🧠 Semantic Memory")
    memory_expander = st.expander("View Long-Term Memories", expanded=False)
    with memory_expander:
        try:
            from memory.semantic_memory import get_memory_stats, retrieve_memories
            
            # Show stats
            stats = get_memory_stats()
            if "error" not in stats:
                st.metric("Total Memories", stats.get("total_memories", 0))
                
                if stats.get("memory_types"):
                    st.write("**By Type:**")
                    for mem_type, count in stats["memory_types"].items():
                        st.caption(f"- {mem_type}: {count}")
                
                # Search memories
                search_query = st.text_input("Search memories:", placeholder="e.g., car prices", key="memory_search")
                if search_query:
                    memories = retrieve_memories(
                        query=search_query,
                        top_k=5,
                        user_id=st.session_state.user_id,
                        min_score=0.6
                    )
                    
                    if memories:
                        st.write(f"**Found {len(memories)} relevant memories:**")
                        for i, mem in enumerate(memories, 1):
                            with st.container():
                                st.caption(f"**{i}. [{mem['memory_type']}]** - Score: {mem['score']:.2f}")
                                st.text(mem['content'][:200] + "..." if len(mem['content']) > 200 else mem['content'])
                                st.caption(f"🕐 {mem['timestamp'][:10]}")
                    else:
                        st.info("No relevant memories found")
            else:
                st.warning("Memory collection not initialized")
        except Exception as e:
            st.error(f"Could not load memories: {e}")
    
    st.divider()
    
    # Quick Upload Section
    st.subheader("📤 Quick Upload")
    upload_tab1, upload_tab2 = st.tabs(["PDF", "CSV"])
    
    with upload_tab1:
        quick_pdf = st.file_uploader("Upload PDF", type=['pdf'], key="quick_pdf", label_visibility="collapsed")
        if quick_pdf:
            if st.button("Store PDF", key="store_quick_pdf"):
                from rag.pdf_processor import process_and_store_pdf
                with st.spinner("Processing..."):
                    result = process_and_store_pdf(quick_pdf, quick_pdf.name, st.session_state.user_id)
                    if result["success"]:
                        st.success(f"✅ {result['chunks_stored']} chunks stored!")
                    else:
                        st.error(result["error"])
    
    with upload_tab2:
        quick_csv = st.file_uploader("Upload CSV", type=['csv'], key="quick_csv", label_visibility="collapsed")
        if quick_csv:
            if st.button("Store CSV", key="store_quick_csv"):
                from database.csv_processor import process_and_store_csv
                with st.spinner("Processing..."):
                    result = process_and_store_csv(quick_csv, quick_csv.name, user_id=st.session_state.user_id)
                    if result["success"]:
                        st.success(f"✅ {result['rows']} rows stored!")
                    else:
                        st.error(result["error"])
    
    st.caption("💡 For advanced options, visit the Documents page")
    
    st.divider()
    
    st.subheader("Session Memory")
    memory_items = get_session_memory(st.session_state.session_id)
    
    if memory_items:
        for item in memory_items:
            with st.expander(f"Turn {item.get('turn', '?')}: {item['type']}", expanded=False):
                st.text(item['content'])
    else:
        st.info("No session memory yet")

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
