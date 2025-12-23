"""import streamlit as st

Lumiere - AI Knowledge Workspaceimport os

Multi-agent RAG system with document management and data analytics

"""# Load Streamlit secrets into environment variables BEFORE any other imports

import streamlit as stif hasattr(st, 'secrets'):

import uuid    for key in ['OPENAI_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_BASE_URL']:

import hashlib        if key in st.secrets:

from datetime import datetime            os.environ[key] = st.secrets[key]

import plotly.graph_objects as go

import plotly.express as pximport uuid

import time

# Imports for graph and agentsimport pandas as pd

from graph.rag_graph import build_graphimport plotly.express as px

from graph.state import AgentStateimport plotly.graph_objects as go

from memory.session_memory import get_session_memory, append_session_memory, clear_session_memoryfrom streamlit_cookies_manager import EncryptedCookieManager

from memory.semantic_memory import store_memory

from graph.rag_graph import build_graph

# Imports for document/CSV managementfrom memory.session_memory import get_session_memory, append_session_memory

from rag.pdf_processor import list_uploaded_documents, process_and_store_pdffrom langfuse import observe

from database.csv_processor import list_all_tables, process_and_store_csv, sanitize_table_name

st.set_page_config(

# Observability    page_title="Lumiere",

from observability.langfuse_client import langfuse    layout="wide",

    page_icon="🌟",

# Page configuration    initial_sidebar_state="expanded"

st.set_page_config()

    page_title="Lumiere - AI Knowledge Workspace",

    page_icon="💡",# ---------------------------

    layout="wide",# Cookie Manager for Persistent User ID

    initial_sidebar_state="expanded"# ---------------------------

)# Initialize cookie manager only once per session

if "cookies" not in st.session_state:

# Custom CSS for better UI    try:

st.markdown("""        st.session_state.cookies = EncryptedCookieManager(

<style>            prefix="lumiere_app_",

    .stAlert {            password=os.environ.get("COOKIE_PASSWORD", "lumiere_secret_key_change_in_production_2024")

        padding: 0.5rem;        )

        margin: 0.5rem 0;        st.session_state.cookies_enabled = True

    }    except Exception as e:

    .mode-badge {        print(f"Cookie manager initialization failed: {e}")

        display: inline-block;        st.session_state.cookies = None

        padding: 0.25rem 0.75rem;        st.session_state.cookies_enabled = False

        border-radius: 1rem;

        font-size: 0.85rem;cookies = st.session_state.cookies

        font-weight: 600;

        margin-bottom: 1rem;# Only use cookies if they're available and ready

    }cookies_ready = cookies is not None and cookies.ready() if st.session_state.get("cookies_enabled", False) else False

    .mode-all-in {

        background-color: #4CAF50;# ---------------------------

        color: white;# User Session Tracking for Langfuse

    }# ---------------------------

    .mode-chat-rag {from datetime import datetime

        background-color: #2196F3;import platform

        color: white;import json

    }import requests

    .mode-data-analyst {

        background-color: #FF9800;# Helper function to get geographic data from IP

        color: white;def get_geo_data():

    }    """Get geographic data based on IP address"""

</style>    try:

""", unsafe_allow_html=True)        # Using ipapi.co for geolocation (free tier)

        response = requests.get('https://ipapi.co/json/', timeout=2)

# ============================================        if response.status_code == 200:

# SESSION STATE INITIALIZATION            data = response.json()

# ============================================            return {

def initialize_session_state():                "country": data.get("country_name", "Unknown"),

    """Initialize all session state variables"""                "country_code": data.get("country_code", "Unknown"),

                    "city": data.get("city", "Unknown"),

    # Generate session ID (new for each browser session)                "region": data.get("region", "Unknown"),

    if "session_id" not in st.session_state:                "timezone": data.get("timezone", "Unknown"),

        st.session_state.session_id = str(uuid.uuid4())                "ip": data.get("ip", "Unknown")

                }

    # User ID will be set after user enters name    except Exception as e:

    if "user_id" not in st.session_state:        print(f"Geo lookup failed: {e}")

        st.session_state.user_id = None    return {

            "country": "Unknown",

    # User name input        "country_code": "Unknown", 

    if "user_name" not in st.session_state:        "city": "Unknown",

        st.session_state.user_name = ""        "region": "Unknown",

            "timezone": "Unknown",

    # Chat messages        "ip": "Unknown"

    if "messages" not in st.session_state:    }

        st.session_state.messages = []

    # ---------------------------

    # Lumiere mode# Persistent User Identity (Cookie-Based or Session-Based)

    if "lumiere_mode" not in st.session_state:# ---------------------------

        st.session_state.lumiere_mode = "all_in"# Get or create persistent user_id from cookie (if available) or use session-based ID

    if "user_id" not in st.session_state:

    # Workflow visibility toggle    cookies_need_save = False

    if "show_workflow" not in st.session_state:    

        st.session_state.show_workflow = False    if cookies_ready:

            # Cookies are available - use persistent ID

    # Graph instance (built once per session)        if "persistent_user_id" not in cookies or not cookies.get("persistent_user_id"):

    if "graph" not in st.session_state:            # First-time visitor: Create new permanent ID

        st.session_state.graph = build_graph()            new_user_id = str(uuid.uuid4())

            cookies["persistent_user_id"] = new_user_id

# ============================================            cookies["first_visit"] = datetime.now().isoformat()

# SIDEBAR RENDERING            cookies["session_count"] = "1"

# ============================================            persistent_user_id = new_user_id

def render_sidebar():            is_new_user = True

    """Render the sidebar with user info, mode selection, and document stats"""            cookies_need_save = True

            else:

    with st.sidebar:            # Returning visitor: Use existing ID from cookie

        st.title("💡 Lumiere")            persistent_user_id = cookies["persistent_user_id"]

        st.caption("AI Knowledge Workspace")            is_new_user = False

            else:

        st.divider()        # Cookies not available - use session-based ID (temporary)

                persistent_user_id = str(uuid.uuid4())

        # ===== USER IDENTIFICATION =====        is_new_user = True

        st.subheader("👤 User Identity")        print("Warning: Cookies not available, using session-based user ID")

            

        user_name = st.text_input(    # Store persistent user_id in session_state (this is what your app uses)

            "Enter your name/ID:",    st.session_state.user_id = persistent_user_id

            value=st.session_state.user_name,    st.session_state.is_new_user = is_new_user

            placeholder="e.g., john_doe",    st.session_state.cookies_need_save = cookies_need_save

            help="Your data is stored per user. Use the same name to access your documents.",else:

            key="user_name_input"    # User ID already in session state

        )    persistent_user_id = st.session_state.user_id

            is_new_user = st.session_state.get("is_new_user", False)

        if user_name and user_name != st.session_state.user_name:

            # Generate consistent user_id from name# ---------------------------

            st.session_state.user_name = user_name# Session Tracking (Analytics - New Each Refresh)

            st.session_state.user_id = hashlib.md5(user_name.encode()).hexdigest()[:16]# ---------------------------

            st.success(f"✅ Logged in as: {user_name}")# Initialize session tracking

            st.rerun()if "session_id" not in st.session_state:

            # Generate new session ID for this page load (for analytics)

        if st.session_state.user_id:    st.session_state.session_id = str(uuid.uuid4())

            st.info(f"**User:** {st.session_state.user_name}\n\n**ID:** `{st.session_state.user_id[:8]}...`")    st.session_state.session_start = datetime.now()

        else:    st.session_state.session_start_iso = datetime.now().isoformat()

            st.warning("⚠️ Please enter your name to start using Lumiere.")    

            st.stop()    # Track session count for this user (only for returning users with cookies)

            if cookies_ready and not is_new_user:

        st.divider()        session_count = int(cookies.get("session_count", "0")) + 1

                cookies["session_count"] = str(session_count)

        # ===== MODE SELECTION =====        st.session_state.cookies_need_save = True

        st.subheader("🎯 Lumiere Mode")    

            # Get geographic data

        mode_options = {    geo_data = get_geo_data()

            "all_in": "🌐 All-In Mode",    

            "chat_rag": "📚 Docs & Chat Mode",    # Initialize feature usage tracking

            "data_analyst": "📊 Data Analytics Mode"    st.session_state.feature_usage = {

        }        "rag_queries": 0,

                "sql_queries": 0,

        lumiere_mode = st.radio(        "visualizations": 0,

            "Select mode:",        "documents_uploaded": 0,

            options=list(mode_options.keys()),        "tables_uploaded": 0,

            format_func=lambda x: mode_options[x],        "feedbacks_given": 0

            index=list(mode_options.keys()).index(st.session_state.lumiere_mode),    }

            key="mode_selector"    

        )    # Initialize error tracking

            st.session_state.error_tracking = {

        if lumiere_mode != st.session_state.lumiere_mode:        "total_errors": 0,

            st.session_state.lumiere_mode = lumiere_mode        "error_types": {},

            st.rerun()        "last_error": None

            }

        # Mode descriptions    

        mode_descriptions = {    # Capture user metadata

            "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",    st.session_state.user_metadata = {

            "chat_rag": "Chat about your uploaded documents only. No SQL or general knowledge.",        "first_visit": datetime.now().isoformat(),

            "data_analyst": "Query CSV data with SQL and automatic visualizations. No general chat."        "user_agent": st.context.headers.get("User-Agent", "Unknown") if hasattr(st, 'context') and hasattr(st.context, 'headers') else "Unknown",

        }        "platform": platform.system(),

                "session_count": 1,

        st.caption(f"ℹ️ {mode_descriptions[lumiere_mode]}")        "country": geo_data["country"],

                "country_code": geo_data["country_code"],

        st.divider()        "city": geo_data["city"],

                "region": geo_data["region"],

        # ===== WORKFLOW TOGGLE =====        "timezone": geo_data["timezone"],

        st.subheader("⚙️ Settings")        "ip": geo_data["ip"]

            }

        show_workflow = st.checkbox(

            "🔄 Show Agent Workflow",# Always initialize tracking dicts if not exist

            value=st.session_state.show_workflow,if "feature_usage" not in st.session_state:

            help="Display agent execution steps in real-time"    st.session_state.feature_usage = {

        )        "rag_queries": 0,

                "sql_queries": 0,

        if show_workflow != st.session_state.show_workflow:        "visualizations": 0,

            st.session_state.show_workflow = show_workflow        "documents_uploaded": 0,

                "tables_uploaded": 0,

        st.divider()        "feedbacks_given": 0

            }

        # ===== QUICK UPLOAD =====

        st.subheader("📤 Quick Upload")if "error_tracking" not in st.session_state:

            st.session_state.error_tracking = {

        with st.expander("Upload PDF", expanded=False):        "total_errors": 0,

            uploaded_pdf = st.file_uploader(        "error_types": {},

                "Choose a PDF file",        "last_error": None

                type=['pdf'],    }

                key="quick_pdf_upload",

                help="Upload a PDF to add to your knowledge base"# Calculate session duration

            )session_duration_seconds = (datetime.now() - st.session_state.session_start).total_seconds()

            session_duration_minutes = round(session_duration_seconds / 60, 2)

            if uploaded_pdf:

                if st.button("📄 Process PDF", key="process_pdf_btn"):# Store user_id and metadata in environment for Langfuse tracking

                    with st.spinner("Processing PDF..."):os.environ["LANGFUSE_USER_ID"] = st.session_state.user_id

                        result = process_and_store_pdf(

                            file=uploaded_pdf,# Store comprehensive metadata as JSON for Langfuse

                            filename=uploaded_pdf.name,if "user_metadata" in st.session_state:

                            user_id=st.session_state.user_id    comprehensive_metadata = {

                        )        **st.session_state.user_metadata,

                                "session_duration_minutes": session_duration_minutes,

                        if result["success"]:        "feature_usage": st.session_state.feature_usage,

                            st.success(f"✅ Stored {result['chunks_stored']} chunks!")        "error_tracking": {

                            st.rerun()            "total_errors": st.session_state.error_tracking["total_errors"],

                        else:            "error_types": list(st.session_state.error_tracking["error_types"].keys())

                            st.error(f"❌ Error: {result['error']}")        }

            }

        with st.expander("Upload CSV", expanded=False):    os.environ["LANGFUSE_USER_METADATA"] = json.dumps(comprehensive_metadata)

            uploaded_csv = st.file_uploader(

                "Choose a CSV file",# ---------------------------

                type=['csv'],# Apple-like Custom CSS

                key="quick_csv_upload",# ---------------------------

                help="Upload a CSV to store in database"st.markdown("""

            )<style>

                /* Apple-inspired color palette and typography */

            if uploaded_csv:    :root {

                table_name = st.text_input(        --apple-blue: #007AFF;

                    "Table name:",        --apple-green: #34C759;

                    value=sanitize_table_name(uploaded_csv.name),        --apple-gray: #86868B;

                    key="quick_csv_table_name"        --apple-dark: #1D1D1F;

                )        --apple-bg: #F5F5F7;

                    }

                if st.button("📊 Store CSV", key="process_csv_btn"):    

                    with st.spinner("Processing CSV..."):    /* Main container styling */

                        result = process_and_store_csv(    .main {

                            file=uploaded_csv,        background-color: var(--apple-bg);

                            filename=uploaded_csv.name,    }

                            table_name=table_name,    

                            if_exists='fail',    /* Header styling */

                            user_id=st.session_state.user_id    h1 {

                        )        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

                                font-weight: 600;

                        if result["success"]:        color: var(--apple-dark);

                            st.success(f"✅ Stored {result['rows']} rows!")        letter-spacing: -0.5px;

                            st.rerun()    }

                        else:    

                            st.error(f"❌ Error: {result['error']}")    /* Subtitle styling */

            .subtitle {

        st.caption("💡 For full document management, visit the [📚 Documents](/Documents) page.")        color: var(--apple-gray);

                font-size: 1.1rem;

        st.divider()        font-weight: 400;

                margin-top: -1rem;

        # ===== DOCUMENT STATS =====        margin-bottom: 2rem;

        st.subheader("📊 Your Data")    }

            

        # Get document count    /* Feature badges */

        try:    .feature-badge {

            documents = list_uploaded_documents(user_id=st.session_state.user_id)        display: inline-block;

            doc_count = len(documents)        padding: 0.3rem 0.8rem;

        except Exception:        margin: 0.2rem;

            doc_count = 0        background: linear-gradient(135deg, var(--apple-blue) 0%, #0051D5 100%);

            documents = []        color: white;

                border-radius: 12px;

        # Get table count        font-size: 0.85rem;

        try:        font-weight: 500;

            tables = list_all_tables(user_id=st.session_state.user_id)        box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);

            table_count = len(tables)    }

        except Exception:    

            table_count = 0    /* Cards with shadow */

            tables = []    .card {

                background: white;

        col1, col2 = st.columns(2)        border-radius: 12px;

        with col1:        padding: 1.5rem;

            st.metric("📄 Documents", doc_count)        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

        with col2:        margin: 1rem 0;

            st.metric("📊 Tables", table_count)    }

            

        # Show document list    /* Sidebar styling */

        if doc_count > 0:    section[data-testid="stSidebar"] {

            with st.expander(f"📄 Documents ({doc_count})", expanded=False):        background-color: #E8E8E8 !important;

                for doc in documents[:5]:        border-right: 1px solid #D1D1D6;

                    st.caption(f"• {doc['filename'][:30]}{'...' if len(doc['filename']) > 30 else ''}")    }

                if doc_count > 5:    

                    st.caption(f"... and {doc_count - 5} more")    /* Sidebar text - all black */

            section[data-testid="stSidebar"] .stMarkdown,

        # Show table list    section[data-testid="stSidebar"] .stMarkdown p,

        if table_count > 0:    section[data-testid="stSidebar"] .stMarkdown h1,

            with st.expander(f"📊 Tables ({table_count})", expanded=False):    section[data-testid="stSidebar"] .stMarkdown h2,

                for table in tables[:5]:    section[data-testid="stSidebar"] .stMarkdown h3,

                    st.caption(f"• {table['table_name']}")    section[data-testid="stSidebar"] .stMarkdown strong,

                if table_count > 5:    section[data-testid="stSidebar"] label,

                    st.caption(f"... and {table_count - 5} more")    section[data-testid="stSidebar"] p,

            section[data-testid="stSidebar"] h1,

        st.divider()    section[data-testid="stSidebar"] h2,

            section[data-testid="stSidebar"] h3,

        # ===== SESSION STATS =====    section[data-testid="stSidebar"] span,

        st.subheader("📈 Session Stats")    section[data-testid="stSidebar"] div {

                color: #000000 !important;

        col1, col2 = st.columns(2)    }

        with col1:    

            st.metric("💬 Messages", len(st.session_state.messages))    /* Sidebar checkbox labels */

        with col2:    section[data-testid="stSidebar"] .stCheckbox label {

            # Count memory items        color: #000000 !important;

            try:    }

                memory_items = get_session_memory(st.session_state.session_id)    

                memory_count = len([m for m in memory_items if m["type"] != "conversation"])    /* Sidebar selectbox */

            except Exception:    section[data-testid="stSidebar"] .stSelectbox label,

                memory_count = 0    section[data-testid="stSidebar"] .stSelectbox div {

            st.metric("🧠 Memories", memory_count)        color: #000000 !important;

            }

        st.divider()    

            /* Sidebar caption text */

        # ===== ACTIONS =====    section[data-testid="stSidebar"] .stCaption {

        st.subheader("🔧 Actions")        color: #000000 !important;

            }

        if st.button("🗑️ Clear Chat History", use_container_width=True):    

            st.session_state.messages = []    /* Sidebar button text */

            clear_session_memory(st.session_state.session_id)    section[data-testid="stSidebar"] button {

            st.success("Chat cleared!")        color: #000000 !important;

            st.rerun()    }

            

        if st.button("🔄 New Session", use_container_width=True):    /* Sidebar metrics */

            # Generate new session ID but keep user_id    section[data-testid="stSidebar"] [data-testid="stMetric"] {

            st.session_state.session_id = str(uuid.uuid4())        background: transparent;

            st.session_state.messages = []        color: #000000 !important;

            st.success("New session started!")    }

            st.rerun()    

            section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {

        st.divider()        color: #000000 !important;

            }

        # ===== FOOTER =====    

        st.caption("🔍 **Observability:** Langfuse enabled")    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {

        st.caption(f"🆔 **Session:** `{st.session_state.session_id[:8]}...`")        color: #000000 !important;

    }

# ============================================    

# VISUALIZATION RENDERING    /* Button styling */

# ============================================    .stButton > button {

def render_visualization(viz_config: dict, sql_results: dict):        border-radius: 10px;

    """Render chart based on visualization configuration"""        font-weight: 500;

            transition: all 0.2s ease;

    if not viz_config or not sql_results:        border: none;

        return        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

        }

    chart_type = viz_config.get("chart_type")    

    x_column = viz_config.get("x_column")    .stButton > button:hover {

    y_column = viz_config.get("y_column")        transform: translateY(-1px);

    title = viz_config.get("title", "Data Visualization")        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

        }

    data = sql_results.get("data", [])    

        /* Metrics styling */

    if not data or not chart_type:    [data-testid="stMetric"] {

        return        background: white;

            padding: 1rem;

    try:        border-radius: 10px;

        # Convert data to dict format for Plotly        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

        if hasattr(data[0], 'keys'):    }

            # Row objects    

            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}    /* Clean expander */

        elif isinstance(data[0], dict):    .streamlit-expanderHeader {

            # Already dicts        background-color: white;

            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}        border-radius: 8px;

        else:        font-weight: 500;

            st.warning("Cannot render visualization: unsupported data format")    }

            return    

            /* Hide Streamlit branding */

        # Create appropriate chart    #MainMenu {visibility: hidden;}

        if chart_type == "bar":    footer {visibility: hidden;}

            fig = go.Figure(data=[    

                go.Bar(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []))    /* Chat input styling */

            ])    .stChatInput {

            fig.update_layout(        border-radius: 12px;

                title=title,    }

                xaxis_title=x_column,</style>

                yaxis_title=y_column,""", unsafe_allow_html=True)

                template="plotly_white"

            )# ---------------------------

            st.plotly_chart(fig, use_container_width=True)# Initialize Sample Data (First Run)

        # ---------------------------

        elif chart_type == "line":@st.cache_resource

            fig = go.Figure(data=[def initialize_app():

                go.Scatter(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []), mode='lines+markers')    """Initialize app resources on first run."""

            ])    try:

            fig.update_layout(        from rag.qdrant_client import client

                title=title,        from rag.collections import ensure_collection_exists

                xaxis_title=x_column,        from config.settings import DOCUMENT_COLLECTION_NAME

                yaxis_title=y_column,        

                template="plotly_white"        # Ensure collections exist

            )        ensure_collection_exists(DOCUMENT_COLLECTION_NAME)

            st.plotly_chart(fig, use_container_width=True)        

                # Check if we need sample data

        elif chart_type == "pie":        collection_info = client.get_collection(DOCUMENT_COLLECTION_NAME)

            fig = go.Figure(data=[        if collection_info.points_count == 0:

                go.Pie(labels=data_dict.get(x_column, []), values=data_dict.get(y_column, []))            print("📚 No documents found. Initializing sample data...")

            ])            from scripts.init_sample_data import initialize_sample_data

            fig.update_layout(title=title, template="plotly_white")            initialize_sample_data()

            st.plotly_chart(fig, use_container_width=True)            return "Sample data initialized"

                else:

        elif chart_type == "scatter":            return f"Ready ({collection_info.points_count} documents)"

            fig = go.Figure(data=[    except Exception as e:

                go.Scatter(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []), mode='markers')        print(f"⚠️ Initialization warning: {e}")

            ])        return "Ready"

            fig.update_layout(

                title=title,# Initialize on first load

                xaxis_title=x_column,init_status = initialize_app()

                yaxis_title=y_column,

                template="plotly_white"# ---------------------------

            )# Helper Functions

            st.plotly_chart(fig, use_container_width=True)# ---------------------------

        def render_chart(viz_config):

        elif chart_type == "histogram":    """Render enhanced visualization with stats sidebar."""

            fig = go.Figure(data=[    if not viz_config:

                go.Histogram(x=data_dict.get(x_column, []))        return

            ])    

            fig.update_layout(    chart_type = viz_config.get("chart_type")

                title=title,    data = viz_config.get("data", [])

                xaxis_title=x_column,    columns = viz_config.get("columns", [])

                yaxis_title="Count",    title = viz_config.get("title", "Data Visualization")

                template="plotly_white"    x_col = viz_config.get("x_column")

            )    y_col = viz_config.get("y_column")

            st.plotly_chart(fig, use_container_width=True)    reasoning = viz_config.get("reasoning", "")

            

        elif chart_type == "table":    if not data or not columns:

            # Just show the data as table        return

            import pandas as pd    

            df = pd.DataFrame(data_dict)    # Convert to DataFrame

            st.dataframe(df, use_container_width=True)    df = pd.DataFrame(data, columns=columns)

            

        else:    st.divider()

            st.info(f"Chart type '{chart_type}' not supported yet.")    st.subheader(f"📊 {title}")

        if reasoning:

    except Exception as e:        st.caption(reasoning)

        st.error(f"Error rendering visualization: {e}")    

    try:

# ============================================        # Modern Plotly theme configuration

# GRAPH INVOCATION        chart_config = {

# ============================================            'displayModeBar': True,

def invoke_graph(user_message: str):            'displaylogo': False,

    """Invoke the LangGraph workflow with proper state management"""            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']

            }

    # Create Langfuse trace        

    trace = langfuse.trace(        # Professional color scheme (Apple-inspired)

        name="lumiere_chat",        colors = ['#007AFF', '#5856D6', '#AF52DE', '#FF2D55', '#FF9500', '#FFCC00', '#34C759', '#00C7BE']

        user_id=st.session_state.user_id,        

        session_id=st.session_state.session_id,        # Layout for chart and stats

        input={"message": user_message, "mode": st.session_state.lumiere_mode},        col_chart, col_stats = st.columns([3, 1])

        metadata={        

            "lumiere_mode": st.session_state.lumiere_mode,        with col_chart:

            "message_count": len(st.session_state.messages),            # Create chart based on type with enhanced styling

            "timestamp": datetime.now().isoformat()            if chart_type == "bar":

        }                fig = px.bar(df, x=x_col, y=y_col, title="")

    )                fig.update_traces(marker_color=colors[0], marker_line_width=0)

                    

    try:            elif chart_type == "line":

        # Build initial state                fig = px.line(df, x=x_col, y=y_col, title="", markers=True)

        initial_state: AgentState = {                fig.update_traces(line_color=colors[0], line_width=3, marker_size=8)

            "messages": [user_message],                

            "session_id": st.session_state.session_id,            elif chart_type == "pie":

            "user_id": st.session_state.user_id,                fig = px.pie(df, names=x_col, values=y_col, title="")

            "lumiere_mode": st.session_state.lumiere_mode,                fig.update_traces(marker=dict(colors=colors, line=dict(color='white', width=2)))

            "question": user_message,                

            "user_input": user_message,            elif chart_type == "scatter":

            "intent": None,                fig = px.scatter(df, x=x_col, y=y_col, title="")

            "needs_rag": False,                fig.update_traces(marker=dict(size=12, color=colors[0], line=dict(width=0)))

            "needs_sql": False,                

            "retrieved_docs": [],            elif chart_type == "histogram":

            "sql_query": None,                fig = px.histogram(df, x=x_col, title="")

            "sql_results": None,                fig.update_traces(marker_color=colors[0], marker_line_width=0)

            "visualization_config": None,            else:

            "answer": None,                # Default to table if unknown type

            "retry_count": 0,                st.dataframe(df, use_container_width=True)

            "decision": None,                return

            "reasoning_mode": None,            

            "memory_signal": None,            # Apply modern styling to all charts

        }            fig.update_layout(

                        plot_bgcolor='rgba(0,0,0,0)',

        # Invoke graph with workflow display                paper_bgcolor='rgba(0,0,0,0)',

        if st.session_state.show_workflow:                font=dict(family="SF Pro Display, -apple-system, system-ui, sans-serif", size=12, color='#1d1d1f'),

            with st.status("🤖 Processing your request...", expanded=True) as status:                margin=dict(l=10, r=10, t=30, b=10),

                st.write("🎯 Classifying intent...")                height=400,

                                showlegend=True,

                # Stream graph execution                legend=dict(

                final_state = None                    orientation="h",

                for state in st.session_state.graph.stream(initial_state):                    yanchor="bottom",

                    # Update status based on state                    y=1.02,

                    if "intent" in state and state.get("intent"):                    xanchor="right",

                        intent = state.get("intent")                    x=1

                        st.write(f"📋 Intent detected: **{intent}**")                ),

                                    xaxis=dict(

                    if state.get("needs_rag"):                    showgrid=True,

                        st.write("📚 Retrieving documents...")                    gridwidth=1,

                                        gridcolor='rgba(0,0,0,0.05)',

                    if state.get("needs_sql"):                    showline=False,

                        st.write("🗄️ Executing SQL query...")                    zeroline=False

                                    ),

                    if state.get("retrieved_docs"):                yaxis=dict(

                        doc_count = len(state.get("retrieved_docs", []))                    showgrid=True,

                        st.write(f"📄 Retrieved {doc_count} documents")                    gridwidth=1,

                                        gridcolor='rgba(0,0,0,0.05)',

                    if state.get("sql_results"):                    showline=False,

                        sql_success = state.get("sql_results", {}).get("success", False)                    zeroline=False

                        if sql_success:                ),

                            row_count = state.get("sql_results", {}).get("row_count", 0)                hovermode='closest'

                            st.write(f"✅ SQL query returned {row_count} rows")            )

                        else:            

                            st.write("❌ SQL query failed")            st.plotly_chart(fig, use_container_width=True, config=chart_config)

                            

                    if state.get("answer"):        with col_stats:

                        st.write("💭 Generating response...")            # Key statistics sidebar with custom styling

                                st.markdown("""

                    if state.get("visualization_config"):                <style>

                        st.write("📊 Creating visualization...")                [data-testid="stMetric"] {

                                        background-color: #f5f5f7;

                    final_state = state                    padding: 1rem;

                                    border-radius: 8px;

                status.update(label="✅ Processing complete!", state="complete")                    margin-bottom: 0.5rem;

        else:                }

            # Execute without workflow display                [data-testid="stMetricLabel"] {

            final_state = None                    color: #1d1d1f !important;

            for state in st.session_state.graph.stream(initial_state):                    font-weight: 500;

                final_state = state                }

                        [data-testid="stMetricValue"] {

        # Extract answer and metadata                    color: #1d1d1f !important;

        answer = final_state.get("answer", "I couldn't generate a response.")                    font-weight: 600;

        sql_results = final_state.get("sql_results")                }

        visualization_config = final_state.get("visualization_config")                </style>

        memory_signal = final_state.get("memory_signal")            """, unsafe_allow_html=True)

                    

        # Store conversation in session memory            st.markdown("### Key Stats")

        append_session_memory(            

            st.session_state.session_id,            # Calculate stats for numeric column (y_col)

            {            if y_col and y_col in df.columns:

                "type": "conversation",                numeric_col = df[y_col]

                "content": f"User: {user_message}",                if pd.api.types.is_numeric_dtype(numeric_col):

                "turn": len(st.session_state.messages) // 2                    total = numeric_col.sum()

            }                    avg = numeric_col.mean()

        )                    max_val = numeric_col.max()

                            min_val = numeric_col.min()

        append_session_memory(                    count = len(numeric_col)

            st.session_state.session_id,                    

            {                    st.metric("Total", f"{total:,.0f}" if total > 100 else f"{total:.2f}")

                "type": "conversation",                    st.metric("Average", f"{avg:,.0f}" if avg > 100 else f"{avg:.2f}")

                "content": f"Assistant: {answer}",                    st.metric("Maximum", f"{max_val:,.0f}" if max_val > 100 else f"{max_val:.2f}")

                "turn": len(st.session_state.messages) // 2                    st.metric("Minimum", f"{min_val:,.0f}" if min_val > 100 else f"{min_val:.2f}")

            }                    st.metric("Count", f"{count:,}")

        )                else:

                            # For non-numeric columns

        # Store memory signal if detected                    unique_count = df[y_col].nunique()

        if memory_signal:                    total_rows = len(df)

            append_session_memory(                    st.metric("Total Rows", f"{total_rows:,}")

                st.session_state.session_id,                    st.metric("Unique Values", f"{unique_count:,}")

                memory_signal            else:

            )                # General stats

                            st.metric("Total Rows", f"{len(df):,}")

            # Also store in semantic memory for long-term recall                st.metric("Columns", len(df.columns))

            try:        

                store_memory(        # Show data table below chart (collapsed by default)

                    content=memory_signal["content"],        with st.expander("📋 View Data Table", expanded=False):

                    memory_type=memory_signal["type"],            st.dataframe(df, use_container_width=True, height=300)

                    user_id=st.session_state.user_id,            

                    session_id=st.session_state.session_id,            # Add download button

                    metadata={            csv = df.to_csv(index=False)

                        "timestamp": datetime.now().isoformat(),            st.download_button(

                        "lumiere_mode": st.session_state.lumiere_mode                label="📥 Download as CSV",

                    }                data=csv,

                )                file_name="query_results.csv",

            except Exception as e:                mime="text/csv",

                print(f"Warning: Failed to store semantic memory: {e}")                use_container_width=True

                    )

        # Update trace    

        trace.update(    except Exception as e:

            output={        st.error(f"Error rendering chart: {e}")

                "answer": answer,        # Fallback to table

                "has_sql": bool(sql_results),        st.dataframe(df, use_container_width=True)

                "has_visualization": bool(visualization_config),

                "memory_signal": memory_signal# ---------------------------

            }# Modern Header

        )# ---------------------------

        col1, col2 = st.columns([3, 1])

        return {with col1:

            "answer": answer,    st.title("Lumiere")

            "sql_results": sql_results,    st.markdown('<p class="subtitle">Intelligent Knowledge Assistant with RAG & Analytics</p>', unsafe_allow_html=True)

            "visualization_config": visualization_config

        }with col2:

        st.markdown("###")  # Spacing

    except Exception as e:    if init_status:

        trace.update(        st.caption(f"✓ {init_status}")

            output={"error": str(e)},

            level="ERROR"# Feature badges

        )st.markdown("""

        st.error(f"❌ Error processing request: {e}")<div style="margin: -1rem 0 1.5rem 0;">

        return {    <span class="feature-badge">RAG-Powered</span>

            "answer": f"I encountered an error: {str(e)}",    <span class="feature-badge">Data Analytics</span>

            "sql_results": None,    <span class="feature-badge">Semantic Memory</span>

            "visualization_config": None</div>

        }""", unsafe_allow_html=True)

    finally:

        trace.end()# ---------------------------

# Settings & Advanced Panel (equal width, before chat)

# ============================================# ---------------------------

# MAIN CHAT INTERFACEcol_settings, col_advanced = st.columns(2)

# ============================================

def render_chat_interface():with col_settings:

    """Render the main chat interface"""    with st.expander("⚙️ Settings", expanded=False):

            col1, col2, col3 = st.columns([2, 2, 1])

    # Show mode badge        

    mode_classes = {        with col1:

        "all_in": "mode-all-in",            # Mode selector

        "chat_rag": "mode-chat-rag",            mode_options = {

        "data_analyst": "mode-data-analyst"                "all_in": "All Features",

    }                "chat_rag": "Chat + Documents",

                    "data_analyst": "Analytics"

    mode_names = {            }

        "all_in": "🌐 All-In Mode",            

        "chat_rag": "📚 Docs & Chat Mode",            selected_mode = st.selectbox(

        "data_analyst": "📊 Data Analytics Mode"                "Mode",

    }                options=list(mode_options.keys()),

                    format_func=lambda x: mode_options[x],

    st.markdown(                index=list(mode_options.keys()).index(st.session_state.get("lumiere_mode", "all_in"))

        f'<div class="mode-badge {mode_classes[st.session_state.lumiere_mode]}">'            )

        f'{mode_names[st.session_state.lumiere_mode]}'            

        f'</div>',            if selected_mode != st.session_state.get("lumiere_mode", "all_in"):

        unsafe_allow_html=True                st.session_state.lumiere_mode = selected_mode

    )                st.rerun()

            

    # Welcome message for new users        with col2:

    if len(st.session_state.messages) == 0:            # Workflow toggle

        st.info("""            show_streaming = st.checkbox("Show Workflow", value=True)

        👋 **Welcome to Lumiere!**        

                with col3:

        **Getting Started:**            # Clear button

        1. ✅ You're logged in as **{name}**            if st.button("Clear Session", use_container_width=True, type="secondary"):

        2. 📁 Upload documents in the sidebar or visit the [📚 Documents](/Documents) page                from memory.session_memory import clear_session_memory

        3. 💬 Start chatting below!                clear_session_memory(st.session_state.session_id)

                        st.session_state.messages = []

        **Current Mode:** {mode}                st.session_state.turn_count = 0

        - {description}                st.rerun()

        

        **Tips:**with col_advanced:

        - Upload PDFs to ask questions about your documents    with st.expander("🔧 Advanced", expanded=False):

        - Upload CSVs to query data with natural language        # Memory search

        - Switch modes in the sidebar for different capabilities        st.caption("**Search Memories**")

        """.format(        try:

            name=st.session_state.user_name,            from memory.semantic_memory import retrieve_memories

            mode=mode_names[st.session_state.lumiere_mode],            

            description={            search_query = st.text_input("Search:", placeholder="e.g., RAG systems", key="memory_search", label_visibility="collapsed")

                "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",            if search_query:

                "chat_rag": "Chat about your uploaded documents only.",                memories = retrieve_memories(

                "data_analyst": "Query CSV data with SQL and automatic visualizations."                    query=search_query,

            }[st.session_state.lumiere_mode]                    top_k=3,

        ))                    user_id=st.session_state.user_id,

                        min_score=0.6

    # Display chat messages                )

    for message in st.session_state.messages:                

        with st.chat_message(message["role"]):                if memories:

            st.markdown(message["content"])                    for i, mem in enumerate(memories, 1):

                                    st.caption(f"**{i}.** {mem['content'][:100]}...")

            # Show visualization if present                        st.caption(f"Score: {mem['score']:.2f} | {mem['timestamp'][:10]}")

            if message["role"] == "assistant" and "visualization" in message:                        if i < len(memories):

                render_visualization(                            st.markdown("---")

                    message["visualization"],                else:

                    message.get("sql_results")                    st.info("No memories found")

                )        except Exception as e:

                st.warning("Memory search unavailable")

    # Chat input        

    if prompt := st.chat_input("Ask me anything..."):        st.markdown("---")

        # Add user message to chat        

        st.session_state.messages.append({"role": "user", "content": prompt})        # Quick upload

                st.caption("**Quick Upload**")

        with st.chat_message("user"):        upload_type = st.radio("Type:", ["PDF", "CSV"], horizontal=True, label_visibility="collapsed")

            st.markdown(prompt)        

                if upload_type == "PDF":

        # Generate response            quick_file = st.file_uploader("Upload", type=['pdf'], key="quick_pdf", label_visibility="collapsed")

        with st.chat_message("assistant"):            if quick_file and st.button("Store", key="store_pdf"):

            response = invoke_graph(prompt)                from rag.pdf_processor import process_and_store_pdf

                            with st.spinner("Processing..."):

            # Display answer                    result = process_and_store_pdf(quick_file, quick_file.name, st.session_state.user_id)

            st.markdown(response["answer"])                    if result["success"]:

                                    st.success(f"✓ {result['chunks_stored']} chunks")

            # Display visualization if present                        st.rerun()

            if response["visualization_config"] and st.session_state.lumiere_mode == "data_analyst":                    else:

                render_visualization(                        st.error(result["error"])

                    response["visualization_config"],        else:

                    response["sql_results"]            quick_file = st.file_uploader("Upload", type=['csv'], key="quick_csv", label_visibility="collapsed")

                )            if quick_file and st.button("Store", key="store_csv"):

                        from database.csv_processor import process_and_store_csv

        # Add assistant message to chat                with st.spinner("Processing..."):

        assistant_message = {                    result = process_and_store_csv(quick_file, quick_file.name, user_id=st.session_state.user_id)

            "role": "assistant",                    if result["success"]:

            "content": response["answer"]                        st.success(f"✓ {result['rows']} rows")

        }                        st.rerun()

                            else:

        if response["visualization_config"]:                        st.error(result["error"])

            assistant_message["visualization"] = response["visualization_config"]        

            assistant_message["sql_results"] = response["sql_results"]        st.caption("💡 Visit Documents page for more options")

        

        st.session_state.messages.append(assistant_message)st.divider()

        

        st.rerun()# ---------------------------

# Session initialization

# ============================================# ---------------------------

# MAIN APPLICATIONif "session_id" not in st.session_state:

# ============================================    st.session_state.session_id = str(uuid.uuid4())

def main():

    """Main application entry point"""if "user_id" not in st.session_state:

        st.session_state.user_id = "streamlit_user"

    # Initialize session state

    initialize_session_state()if "messages" not in st.session_state:

        st.session_state.messages = []

    # Render sidebar

    render_sidebar()if "turn_count" not in st.session_state:

        st.session_state.turn_count = 0

    # Main content area

    st.title("💡 Lumiere")if "graph" not in st.session_state:

    st.caption("AI Knowledge Workspace - Multi-Agent RAG System")    st.session_state.graph = build_graph()

    

    # Render chat interfaceif "lumiere_mode" not in st.session_state:

    render_chat_interface()    st.session_state.lumiere_mode = "all_in"  # Default mode



if __name__ == "__main__":# ---------------------------

    main()# Clean Sidebar (Documents & Tables only)

# ---------------------------
with st.sidebar:
    
    # Document Library (PDFs only)
    st.markdown("### Documents")
    
    try:
        from rag.qdrant_client import get_client
        from rag.collections import get_user_collection_name
        
        # Get user-specific collection name
        collection_name = get_user_collection_name(st.session_state.user_id, "documents")
        
        # Scroll all documents with their metadata
        client = get_client()
        docs = client.scroll(
            collection_name=collection_name,
            limit=100,
            with_payload=True,
            with_vectors=False
        )[0]
        
        pdf_docs = set()
        sample_docs = set()
        
        if docs:
            for doc in docs:
                if doc.payload:
                    filename = doc.payload.get("filename")
                    doc_type = doc.payload.get("document_type")
                    
                    # Check for PDF documents
                    if filename and doc_type == "pdf":
                        pdf_docs.add(filename)
                    # Check for sample documents
                    elif not filename:
                        source = doc.payload.get("source", "")
                        if " (Sample Document)" in source:
                            title = source.replace(" (Sample Document)", "")
                            sample_docs.add(title)
                        elif source:
                            sample_docs.add(source)
            
            # Display PDFs and samples
            all_docs = sorted(list(pdf_docs)) + sorted(list(sample_docs))
            if all_docs:
                for idx, doc_name in enumerate(all_docs, 1):
                    st.markdown(f"**{idx}.** {doc_name}")
            else:
                st.caption("No documents")
        else:
            st.caption("No documents")
            
    except Exception as e:
        st.caption("Unable to load")
    
    st.divider()
    
    # Tables (CSVs)
    st.markdown("### Tables")
    
    try:
        from database.sqlite_client import get_user_client
        
        # Get user-specific database client
        db_client = get_user_client(st.session_state.user_id)
        
        # Get all tables from SQLite using the list_tables method
        tables = db_client.list_tables()
        
        # Filter out system tables
        user_tables = [t for t in tables if not t.startswith('sqlite_')]
        
        if user_tables:
            for idx, table_name in enumerate(user_tables, 1):
                st.markdown(f"**{idx}.** {table_name}")
        else:
            st.caption("No tables")
            
    except Exception as e:
        st.caption(f"Unable to load: {str(e)}")
    
    st.divider()
    
    # User Session Info (for monitoring/debugging)
    with st.expander("🔍 Session Analytics", expanded=False):
        # Basic Info
        st.markdown("### 👤 User Info")
        st.caption("**Persistent User ID:** 🍪")
        st.code(st.session_state.user_id[:16] + "...", language=None)
        if is_new_user:
            st.success("✨ New user - Welcome!")
        else:
            st.info("👋 Returning user - Data restored from cookie")
        
        # Session Stats
        st.markdown("### 📊 Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            session_count_display = int(cookies.get("session_count", "1")) if cookies_ready else 1
            st.metric("Session Count", session_count_display)
            st.metric("Duration", f"{session_duration_minutes} min")
        with col2:
            st.metric("Total Errors", st.session_state.error_tracking["total_errors"])
            st.metric("Feedbacks", st.session_state.feature_usage.get("feedbacks_given", 0))
        
        # Geographic Info
        if "user_metadata" in st.session_state:
            metadata = st.session_state.user_metadata
            st.markdown("### 🌍 Location")
            st.text(f"🌎 {metadata.get('city', 'Unknown')}, {metadata.get('country', 'Unknown')}")
            st.text(f"🕐 {metadata.get('timezone', 'Unknown')}")
        
        # Feature Usage
        st.markdown("### 🎯 Feature Usage")
        usage = st.session_state.feature_usage
        st.text(f"💬 RAG Queries: {usage.get('rag_queries', 0)}")
        st.text(f"🗄️ SQL Queries: {usage.get('sql_queries', 0)}")
        st.text(f"📊 Visualizations: {usage.get('visualizations', 0)}")
        st.text(f"📄 Docs Uploaded: {usage.get('documents_uploaded', 0)}")
        st.text(f"📋 Tables Uploaded: {usage.get('tables_uploaded', 0)}")
        
        # Timestamps
        st.markdown("### ⏰ Timestamps")
        if "user_metadata" in st.session_state:
            st.caption("**First Visit:**")
            st.text(metadata.get("first_visit", "N/A")[:19])
            
            if "last_visit" in metadata:
                st.caption("**Last Visit:**")
                st.text(metadata["last_visit"][:19])
        
        # Tech Info
        st.markdown("### 💻 Technical")
        st.text(f"Platform: {metadata.get('platform', 'Unknown')}")
        user_agent = metadata.get("user_agent", "Unknown")
        st.text(f"Browser: {user_agent[:40]}...")

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
                
                # Add comprehensive user metadata
                if "user_metadata" in st.session_state:
                    metadata = st.session_state.user_metadata
                    span.set_attribute("user.first_visit", metadata.get("first_visit", ""))
                    span.set_attribute("user.session_count", metadata.get("session_count", 0))
                    span.set_attribute("user.user_agent", metadata.get("user_agent", "Unknown"))
                    span.set_attribute("user.platform", metadata.get("platform", "Unknown"))
                    span.set_attribute("user.country", metadata.get("country", "Unknown"))
                    span.set_attribute("user.city", metadata.get("city", "Unknown"))
                    span.set_attribute("user.timezone", metadata.get("timezone", "Unknown"))
                    if "last_visit" in metadata:
                        span.set_attribute("user.last_visit", metadata["last_visit"])
                
                # Add session analytics
                span.set_attribute("session.duration_minutes", session_duration_minutes)
                span.set_attribute("session.total_errors", st.session_state.error_tracking["total_errors"])
                
                # Add feature usage
                usage = st.session_state.feature_usage
                span.set_attribute("features.rag_queries", usage.get("rag_queries", 0))
                span.set_attribute("features.sql_queries", usage.get("sql_queries", 0))
                span.set_attribute("features.visualizations", usage.get("visualizations", 0))
            
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
            
            # Track feature usage based on query type
            intent = result.get("intent", "unknown")
            if intent == "data_analysis":
                st.session_state.feature_usage["sql_queries"] = st.session_state.feature_usage.get("sql_queries", 0) + 1
            elif result.get("needs_rag"):
                st.session_state.feature_usage["rag_queries"] = st.session_state.feature_usage.get("rag_queries", 0) + 1
            
            # Track visualization
            viz_config = result.get("visualization_config")
            if viz_config and viz_config.get("chart_type") != "table":
                st.session_state.feature_usage["visualizations"] = st.session_state.feature_usage.get("visualizations", 0) + 1
            
            # Display the final answer
            answer_container.markdown(answer)
            
            # Display visualization if available (Data Analyst mode)
            if viz_config and viz_config.get("chart_type") != "table":
                render_chart(viz_config)
            
        except Exception as e:
            error_msg = str(e)
            
            # Track error
            st.session_state.error_tracking["total_errors"] += 1
            st.session_state.error_tracking["last_error"] = error_msg
            error_type = type(e).__name__
            st.session_state.error_tracking["error_types"][error_type] = st.session_state.error_tracking["error_types"].get(error_type, 0) + 1
            
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
    
    # Add feedback component after answer
    st.markdown("---")
    st.markdown("**Was this answer helpful?**")
    feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 8])
    
    with feedback_col1:
        if st.button("👍", key=f"thumbs_up_{st.session_state.turn_count}", help="Helpful"):
            st.session_state.feature_usage["feedbacks_given"] = st.session_state.feature_usage.get("feedbacks_given", 0) + 1
            # Store feedback in memory
            append_session_memory(
                session_id=st.session_state.session_id,
                item={
                    "type": "feedback",
                    "rating": "positive",
                    "turn": st.session_state.turn_count,
                    "query": user_input,
                    "answer": answer
                }
            )
            st.success("Thanks for your feedback!")
    
    with feedback_col2:
        if st.button("👎", key=f"thumbs_down_{st.session_state.turn_count}", help="Not helpful"):
            st.session_state.feature_usage["feedbacks_given"] = st.session_state.feature_usage.get("feedbacks_given", 0) + 1
            # Store negative feedback
            append_session_memory(
                session_id=st.session_state.session_id,
                item={
                    "type": "feedback",
                    "rating": "negative",
                    "turn": st.session_state.turn_count,
                    "query": user_input,
                    "answer": answer
                }
            )
            st.warning("Thanks for your feedback. We'll work on improving!")

# ---------------------------
# Save cookies at the end (after all UI is rendered)
# ---------------------------
# This prevents the save from blocking the chat interface display
if cookies_ready and st.session_state.get("cookies_need_save", False) and not st.session_state.get("cookies_saved", False):
    cookies.save()
    st.session_state.cookies_need_save = False
    st.session_state.cookies_saved = True
