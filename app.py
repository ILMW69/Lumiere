"""
Lumiere - AI Knowledge Workspace
Multi-agent RAG system with document management and data analytics
"""
import streamlit as st
import uuid
import hashlib
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Imports for graph and agents
from graph.rag_graph import build_graph
from graph.state import AgentState
from memory.session_memory import get_session_memory, append_session_memory, clear_session_memory
from memory.semantic_memory import store_memory

# Imports for document/CSV management
from rag.pdf_processor import list_uploaded_documents, process_and_store_pdf
from database.csv_processor import list_all_tables, process_and_store_csv, sanitize_table_name

# Observability
from observability.langfuse_client import langfuse, langfuse_context

# Page configuration
st.set_page_config(
    page_title="Lumiere - AI Knowledge Workspace",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stAlert {
        padding: 0.5rem;
        margin: 0.5rem 0;
    }
    .mode-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .mode-all-in {
        background-color: #4CAF50;
        color: white;
    }
    .mode-chat-rag {
        background-color: #2196F3;
        color: white;
    }
    .mode-data-analyst {
        background-color: #FF9800;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def initialize_session_state():
    """Initialize all session state variables"""
    
    # Generate session ID (new for each browser session)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # User ID will be set after user enters name
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    # User name input
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    # Chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Lumiere mode
    if "lumiere_mode" not in st.session_state:
        st.session_state.lumiere_mode = "all_in"
    
    # Workflow visibility toggle
    if "show_workflow" not in st.session_state:
        st.session_state.show_workflow = False
    
    # Graph instance (built once per session)
    if "graph" not in st.session_state:
        st.session_state.graph = build_graph()

# ============================================
# SIDEBAR RENDERING
# ============================================
def render_sidebar():
    """Render the sidebar with user info, mode selection, and document stats"""
    
    with st.sidebar:
        st.title("💡 Lumiere")
        st.caption("AI Knowledge Workspace")
        
        st.divider()
        
        # ===== USER IDENTIFICATION =====
        st.subheader("👤 User Identity")
        
        user_name = st.text_input(
            "Enter your name/ID:",
            value=st.session_state.user_name,
            placeholder="e.g., john_doe",
            help="Your data is stored per user. Use the same name to access your documents.",
            key="user_name_input"
        )
        
        if user_name and user_name != st.session_state.user_name:
            # Generate consistent user_id from name
            st.session_state.user_name = user_name
            st.session_state.user_id = hashlib.md5(user_name.encode()).hexdigest()[:16]
            st.success(f"✅ Logged in as: {user_name}")
            st.rerun()
        
        if st.session_state.user_id:
            st.info(f"**User:** {st.session_state.user_name}\n\n**ID:** `{st.session_state.user_id[:8]}...`")
        else:
            st.warning("⚠️ Please enter your name to start using Lumiere.")
            st.stop()
        
        st.divider()
        
        # ===== MODE SELECTION =====
        st.subheader("🎯 Lumiere Mode")
        
        mode_options = {
            "all_in": "🌐 All-In Mode",
            "chat_rag": "📚 Docs & Chat Mode",
            "data_analyst": "📊 Data Analytics Mode"
        }
        
        lumiere_mode = st.radio(
            "Select mode:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=list(mode_options.keys()).index(st.session_state.lumiere_mode),
            key="mode_selector"
        )
        
        if lumiere_mode != st.session_state.lumiere_mode:
            st.session_state.lumiere_mode = lumiere_mode
            st.rerun()
        
        # Mode descriptions
        mode_descriptions = {
            "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",
            "chat_rag": "Chat about your uploaded documents only. No SQL or general knowledge.",
            "data_analyst": "Query CSV data with SQL and automatic visualizations. No general chat."
        }
        
        st.caption(f"ℹ️ {mode_descriptions[lumiere_mode]}")
        
        st.divider()
        
        # ===== WORKFLOW TOGGLE =====
        st.subheader("⚙️ Settings")
        
        show_workflow = st.checkbox(
            "🔄 Show Agent Workflow",
            value=st.session_state.show_workflow,
            help="Display agent execution steps in real-time"
        )
        
        if show_workflow != st.session_state.show_workflow:
            st.session_state.show_workflow = show_workflow
        
        st.divider()
        
        # ===== QUICK UPLOAD =====
        st.subheader("📤 Quick Upload")
        
        with st.expander("Upload PDF", expanded=False):
            uploaded_pdf = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                key="quick_pdf_upload",
                help="Upload a PDF to add to your knowledge base"
            )
            
            if uploaded_pdf:
                if st.button("📄 Process PDF", key="process_pdf_btn"):
                    with st.spinner("Processing PDF..."):
                        result = process_and_store_pdf(
                            file=uploaded_pdf,
                            filename=uploaded_pdf.name,
                            user_id=st.session_state.user_id
                        )
                        
                        if result["success"]:
                            st.success(f"✅ Stored {result['chunks_stored']} chunks!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result['error']}")
        
        with st.expander("Upload CSV", expanded=False):
            uploaded_csv = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                key="quick_csv_upload",
                help="Upload a CSV to store in database"
            )
            
            if uploaded_csv:
                table_name = st.text_input(
                    "Table name:",
                    value=sanitize_table_name(uploaded_csv.name),
                    key="quick_csv_table_name"
                )
                
                if st.button("📊 Store CSV", key="process_csv_btn"):
                    with st.spinner("Processing CSV..."):
                        result = process_and_store_csv(
                            file=uploaded_csv,
                            filename=uploaded_csv.name,
                            table_name=table_name,
                            if_exists='fail',
                            user_id=st.session_state.user_id
                        )
                        
                        if result["success"]:
                            st.success(f"✅ Stored {result['rows']} rows!")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result['error']}")
        
        st.caption("💡 For full document management, visit the [📚 Documents](/Documents) page.")
        
        st.divider()
        
        # ===== DOCUMENT STATS =====
        st.subheader("📊 Your Data")
        
        # Get document count
        try:
            documents = list_uploaded_documents(user_id=st.session_state.user_id)
            doc_count = len(documents)
        except Exception:
            doc_count = 0
            documents = []
        
        # Get table count
        try:
            tables = list_all_tables(user_id=st.session_state.user_id)
            table_count = len(tables)
        except Exception:
            table_count = 0
            tables = []
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Documents", doc_count)
        with col2:
            st.metric("�� Tables", table_count)
        
        # Show document list
        if doc_count > 0:
            with st.expander(f"📄 Documents ({doc_count})", expanded=False):
                for doc in documents[:5]:
                    st.caption(f"• {doc['filename'][:30]}{'...' if len(doc['filename']) > 30 else ''}")
                if doc_count > 5:
                    st.caption(f"... and {doc_count - 5} more")
        
        # Show table list
        if table_count > 0:
            with st.expander(f"📊 Tables ({table_count})", expanded=False):
                for table in tables[:5]:
                    st.caption(f"• {table['table_name']}")
                if table_count > 5:
                    st.caption(f"... and {table_count - 5} more")
        
        st.divider()
        
        # ===== SESSION STATS =====
        st.subheader("📈 Session Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Messages", len(st.session_state.messages))
        with col2:
            # Count memory items
            try:
                memory_items = get_session_memory(st.session_state.session_id)
                memory_count = len([m for m in memory_items if m["type"] != "conversation"])
            except Exception:
                memory_count = 0
            st.metric("🧠 Memories", memory_count)
        
        st.divider()
        
        # ===== ACTIONS =====
        st.subheader("🔧 Actions")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            clear_session_memory(st.session_state.session_id)
            st.success("Chat cleared!")
            st.rerun()
        
        if st.button("🔄 New Session", use_container_width=True):
            # Generate new session ID but keep user_id
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.success("New session started!")
            st.rerun()
        
        st.divider()
        
        # ===== FOOTER =====
        observability_status = "✅ enabled" if langfuse else "⚠️ disabled"
        st.caption(f"🔍 **Observability:** Langfuse {observability_status}")
        st.caption(f"🆔 **Session:** `{st.session_state.session_id[:8]}...`")

# ============================================
# VISUALIZATION RENDERING
# ============================================
def render_visualization(viz_config: dict, sql_results: dict):
    """Render chart based on visualization configuration"""
    
    if not viz_config or not sql_results:
        return
    
    chart_type = viz_config.get("chart_type")
    x_column = viz_config.get("x_column")
    y_column = viz_config.get("y_column")
    title = viz_config.get("title", "Data Visualization")
    
    data = sql_results.get("data", [])
    
    if not data or not chart_type:
        return
    
    try:
        # Convert data to dict format for Plotly
        if hasattr(data[0], 'keys'):
            # Row objects
            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}
        elif isinstance(data[0], dict):
            # Already dicts
            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}
        else:
            st.warning("Cannot render visualization: unsupported data format")
            return
        
        # Create appropriate chart
        if chart_type == "bar":
            fig = go.Figure(data=[
                go.Bar(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []))
            ])
            fig.update_layout(
                title=title,
                xaxis_title=x_column,
                yaxis_title=y_column,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "line":
            fig = go.Figure(data=[
                go.Scatter(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []), mode='lines+markers')
            ])
            fig.update_layout(
                title=title,
                xaxis_title=x_column,
                yaxis_title=y_column,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "pie":
            fig = go.Figure(data=[
                go.Pie(labels=data_dict.get(x_column, []), values=data_dict.get(y_column, []))
            ])
            fig.update_layout(title=title, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "scatter":
            fig = go.Figure(data=[
                go.Scatter(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []), mode='markers')
            ])
            fig.update_layout(
                title=title,
                xaxis_title=x_column,
                yaxis_title=y_column,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "histogram":
            fig = go.Figure(data=[
                go.Histogram(x=data_dict.get(x_column, []))
            ])
            fig.update_layout(
                title=title,
                xaxis_title=x_column,
                yaxis_title="Count",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "table":
            # Just show the data as table
            import pandas as pd
            df = pd.DataFrame(data_dict)
            st.dataframe(df, use_container_width=True)
        
        else:
            st.info(f"Chart type '{chart_type}' not supported yet.")
    
    except Exception as e:
        st.error(f"Error rendering visualization: {e}")

# ============================================
# GRAPH INVOCATION
# ============================================
def invoke_graph(user_message: str):
    """Invoke the LangGraph workflow with proper state management"""
    
    # Create Langfuse generation/trace
    generation = None
    if langfuse:
        try:
            # Use generation() which is the correct method in Langfuse 2.0+
            generation = langfuse.generation(
                name="lumiere_chat",
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id,
                input={"message": user_message, "mode": st.session_state.lumiere_mode},
                metadata={
                    "lumiere_mode": st.session_state.lumiere_mode,
                    "message_count": len(st.session_state.messages),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            # Silently continue if Langfuse tracing fails
            generation = None
    else:
        generation = None
    
    try:
        # Build initial state
        initial_state: AgentState = {
            "messages": [user_message],
            "session_id": st.session_state.session_id,
            "user_id": st.session_state.user_id,
            "lumiere_mode": st.session_state.lumiere_mode,
            "question": user_message,
            "user_input": user_message,
            "intent": None,
            "needs_rag": False,
            "needs_sql": False,
            "retrieved_docs": [],
            "sql_query": None,
            "sql_results": None,
            "visualization_config": None,
            "answer": None,
            "retry_count": 0,
            "decision": None,
            "reasoning_mode": None,
            "memory_signal": None,
        }
        
        # Invoke graph with workflow display
        if st.session_state.show_workflow:
            with st.status("🤖 Processing your request...", expanded=True) as status:
                st.write("🎯 Classifying intent...")
                
                # Stream graph execution
                final_state = None
                for output in st.session_state.graph.stream(initial_state):
                    # Each output is a dict with node name as key
                    for node_name, node_output in output.items():
                        # Update status based on node output
                        if isinstance(node_output, dict):
                            if node_output.get("intent"):
                                intent = node_output.get("intent")
                                st.write(f"📋 Intent detected: **{intent}**")
                            
                            if node_output.get("needs_rag"):
                                st.write("📚 Retrieving documents...")
                            
                            if node_output.get("needs_sql"):
                                st.write("🗄️ Executing SQL query...")
                            
                            if node_output.get("retrieved_docs"):
                                doc_count = len(node_output.get("retrieved_docs", []))
                                st.write(f"📄 Retrieved {doc_count} documents")
                            
                            if node_output.get("sql_results"):
                                sql_success = node_output.get("sql_results", {}).get("success", False)
                                if sql_success:
                                    row_count = node_output.get("sql_results", {}).get("row_count", 0)
                                    st.write(f"✅ SQL query returned {row_count} rows")
                                else:
                                    st.write("❌ SQL query failed")
                            
                            if node_output.get("answer"):
                                st.write("💭 Generating response...")
                            
                            if node_output.get("visualization_config"):
                                st.write("📊 Creating visualization...")
                            
                            # Keep updating final_state with the latest node output
                            final_state = node_output
                
                status.update(label="✅ Processing complete!", state="complete")
        else:
            # Execute without workflow display - use invoke for final state
            final_state = st.session_state.graph.invoke(initial_state)
        
        # Extract answer and metadata
        answer = final_state.get("answer", "I couldn't generate a response.")
        sql_results = final_state.get("sql_results")
        visualization_config = final_state.get("visualization_config")
        memory_signal = final_state.get("memory_signal")
        
        # Store conversation in session memory
        append_session_memory(
            st.session_state.session_id,
            {
                "type": "conversation",
                "content": f"User: {user_message}",
                "turn": len(st.session_state.messages) // 2
            }
        )
        
        append_session_memory(
            st.session_state.session_id,
            {
                "type": "conversation",
                "content": f"Assistant: {answer}",
                "turn": len(st.session_state.messages) // 2
            }
        )
        
        # Store memory signal if detected
        if memory_signal:
            append_session_memory(
                st.session_state.session_id,
                memory_signal
            )
            
            # Also store in semantic memory for long-term recall
            try:
                store_memory(
                    content=memory_signal["content"],
                    memory_type=memory_signal["type"],
                    user_id=st.session_state.user_id,
                    session_id=st.session_state.session_id,
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "lumiere_mode": st.session_state.lumiere_mode
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to store semantic memory: {e}")
        
        # Update generation with output
        if generation:
            try:
                generation.update(
                    output={
                        "answer": answer,
                        "has_sql": bool(sql_results),
                        "has_visualization": bool(visualization_config),
                        "memory_signal": memory_signal
                    }
                )
            except Exception as e:
                pass  # Silently ignore Langfuse errors
        
        # Flush Langfuse events
        if langfuse:
            try:
                langfuse.flush()
            except Exception:
                pass
        
        return {
            "answer": answer,
            "sql_results": sql_results,
            "visualization_config": visualization_config
        }
    
    except Exception as e:
        if generation:
            try:
                generation.update(
                    output={"error": str(e)},
                    level="ERROR"
                )
            except Exception:
                pass  # Silently ignore Langfuse errors
        
        # Flush Langfuse events
        if langfuse:
            try:
                langfuse.flush()
            except Exception:
                pass
        
        st.error(f"❌ Error processing request: {e}")
        return {
            "answer": f"I encountered an error: {str(e)}",
            "sql_results": None,
            "visualization_config": None
        }
    finally:
        if generation:
            try:
                generation.end()
            except Exception:
                pass  # Silently ignore Langfuse errors
        
        # Final flush
        if langfuse:
            try:
                langfuse.flush()
            except Exception:
                pass

# ============================================
# MAIN CHAT INTERFACE
# ============================================
def render_chat_interface():
    """Render the main chat interface"""
    
    # Show mode badge
    mode_classes = {
        "all_in": "mode-all-in",
        "chat_rag": "mode-chat-rag",
        "data_analyst": "mode-data-analyst"
    }
    
    mode_names = {
        "all_in": "🌐 All-In Mode",
        "chat_rag": "📚 Docs & Chat Mode",
        "data_analyst": "📊 Data Analytics Mode"
    }
    
    st.markdown(
        f'<div class="mode-badge {mode_classes[st.session_state.lumiere_mode]}">'
        f'{mode_names[st.session_state.lumiere_mode]}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Welcome message for new users
    if len(st.session_state.messages) == 0:
        mode_desc = {
            "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",
            "chat_rag": "Chat about your uploaded documents only.",
            "data_analyst": "Query CSV data with SQL and automatic visualizations."
        }[st.session_state.lumiere_mode]
        
        st.info(f"""
        👋 **Welcome to Lumiere!**
        
        **Getting Started:**
        1. ✅ You're logged in as **{st.session_state.user_name}**
        2. 📁 Upload documents in the sidebar or visit the [📚 Documents](/Documents) page
        3. 💬 Start chatting below!
        
        **Current Mode:** {mode_names[st.session_state.lumiere_mode]}
        - {mode_desc}
        
        **Tips:**
        - Upload PDFs to ask questions about your documents
        - Upload CSVs to query data with natural language
        - Switch modes in the sidebar for different capabilities
        """)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show visualization if present
            if message["role"] == "assistant" and "visualization" in message:
                render_visualization(
                    message["visualization"],
                    message.get("sql_results")
                )
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            response = invoke_graph(prompt)
            
            # Display answer
            st.markdown(response["answer"])
            
            # Display visualization if present
            if response["visualization_config"] and st.session_state.lumiere_mode == "data_analyst":
                render_visualization(
                    response["visualization_config"],
                    response["sql_results"]
                )
        
        # Add assistant message to chat
        assistant_message = {
            "role": "assistant",
            "content": response["answer"]
        }
        
        if response["visualization_config"]:
            assistant_message["visualization"] = response["visualization_config"]
            assistant_message["sql_results"] = response["sql_results"]
        
        st.session_state.messages.append(assistant_message)
        
        st.rerun()

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.title("💡 Lumiere")
    st.caption("AI Knowledge Workspace - Multi-Agent RAG System")
    
    # Render chat interface
    render_chat_interface()

if __name__ == "__main__":
    main()
