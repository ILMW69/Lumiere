""""""import streamlit as st

Lumiere - AI Knowledge Workspace

Multi-agent RAG system with document management and data analyticsLumiere - AI Knowledge Workspaceimport os

"""

import streamlit as stMulti-agent RAG system with document management and data analytics

import uuid

import hashlib"""# Load Streamlit secrets into environment variables BEFORE any other imports

from datetime import datetime

import plotly.graph_objects as goimport streamlit as stif hasattr(st, 'secrets'):

import plotly.express as px

import uuid    for key in ['OPENAI_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY', 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_BASE_URL']:

# Imports for graph and agents

from graph.rag_graph import build_graphimport hashlib        if key in st.secrets:

from graph.state import AgentState

from memory.session_memory import get_session_memory, append_session_memory, clear_session_memoryfrom datetime import datetime            os.environ[key] = st.secrets[key]

from memory.semantic_memory import store_memory

import plotly.graph_objects as go

# Imports for document/CSV management

from rag.pdf_processor import list_uploaded_documents, process_and_store_pdfimport plotly.express as pximport uuid

from database.csv_processor import list_all_tables, process_and_store_csv, sanitize_table_name

import time

# Observability

from observability.langfuse_client import langfuse# Imports for graph and agentsimport pandas as pd



# Page configurationfrom graph.rag_graph import build_graphimport plotly.express as px

st.set_page_config(

    page_title="Lumiere - AI Knowledge Workspace",from graph.state import AgentStateimport plotly.graph_objects as go

    page_icon="💡",

    layout="wide",from memory.session_memory import get_session_memory, append_session_memory, clear_session_memoryfrom streamlit_cookies_manager import EncryptedCookieManager

    initial_sidebar_state="expanded"

)from memory.semantic_memory import store_memory



# Custom CSS for better UIfrom graph.rag_graph import build_graph

st.markdown("""

<style># Imports for document/CSV managementfrom memory.session_memory import get_session_memory, append_session_memory

    .stAlert {

        padding: 0.5rem;from rag.pdf_processor import list_uploaded_documents, process_and_store_pdffrom langfuse import observe

        margin: 0.5rem 0;

    }from database.csv_processor import list_all_tables, process_and_store_csv, sanitize_table_name

    .mode-badge {

        display: inline-block;st.set_page_config(

        padding: 0.25rem 0.75rem;

        border-radius: 1rem;# Observability    page_title="Lumiere",

        font-size: 0.85rem;

        font-weight: 600;from observability.langfuse_client import langfuse    layout="wide",

        margin-bottom: 1rem;

    }    page_icon="🌟",

    .mode-all-in {

        background-color: #4CAF50;# Page configuration    initial_sidebar_state="expanded"

        color: white;

    }st.set_page_config()

    .mode-chat-rag {

        background-color: #2196F3;    page_title="Lumiere - AI Knowledge Workspace",

        color: white;

    }    page_icon="💡",# ---------------------------

    .mode-data-analyst {

        background-color: #FF9800;    layout="wide",# Cookie Manager for Persistent User ID

        color: white;

    }    initial_sidebar_state="expanded"# ---------------------------

</style>

""", unsafe_allow_html=True))# Initialize cookie manager only once per session



# ============================================if "cookies" not in st.session_state:

# SESSION STATE INITIALIZATION

# ============================================# Custom CSS for better UI    try:

def initialize_session_state():

    """Initialize all session state variables"""st.markdown("""        st.session_state.cookies = EncryptedCookieManager(

    

    # Generate session ID (new for each browser session)<style>            prefix="lumiere_app_",

    if "session_id" not in st.session_state:

        st.session_state.session_id = str(uuid.uuid4())    .stAlert {            password=os.environ.get("COOKIE_PASSWORD", "lumiere_secret_key_change_in_production_2024")

    

    # User ID will be set after user enters name        padding: 0.5rem;        )

    if "user_id" not in st.session_state:

        st.session_state.user_id = None        margin: 0.5rem 0;        st.session_state.cookies_enabled = True

    

    # User name input    }    except Exception as e:

    if "user_name" not in st.session_state:

        st.session_state.user_name = ""    .mode-badge {        print(f"Cookie manager initialization failed: {e}")

    

    # Chat messages        display: inline-block;        st.session_state.cookies = None

    if "messages" not in st.session_state:

        st.session_state.messages = []        padding: 0.25rem 0.75rem;        st.session_state.cookies_enabled = False

    

    # Lumiere mode        border-radius: 1rem;

    if "lumiere_mode" not in st.session_state:

        st.session_state.lumiere_mode = "all_in"        font-size: 0.85rem;cookies = st.session_state.cookies

    

    # Workflow visibility toggle        font-weight: 600;

    if "show_workflow" not in st.session_state:

        st.session_state.show_workflow = False        margin-bottom: 1rem;# Only use cookies if they're available and ready

    

    # Graph instance (built once per session)    }cookies_ready = cookies is not None and cookies.ready() if st.session_state.get("cookies_enabled", False) else False

    if "graph" not in st.session_state:

        st.session_state.graph = build_graph()    .mode-all-in {



# ============================================        background-color: #4CAF50;# ---------------------------

# SIDEBAR RENDERING

# ============================================        color: white;# User Session Tracking for Langfuse

def render_sidebar():

    """Render the sidebar with user info, mode selection, and document stats"""    }# ---------------------------

    

    with st.sidebar:    .mode-chat-rag {from datetime import datetime

        st.title("💡 Lumiere")

        st.caption("AI Knowledge Workspace")        background-color: #2196F3;import platform

        

        st.divider()        color: white;import json

        

        # ===== USER IDENTIFICATION =====    }import requests

        st.subheader("👤 User Identity")

            .mode-data-analyst {

        user_name = st.text_input(

            "Enter your name/ID:",        background-color: #FF9800;# Helper function to get geographic data from IP

            value=st.session_state.user_name,

            placeholder="e.g., john_doe",        color: white;def get_geo_data():

            help="Your data is stored per user. Use the same name to access your documents.",

            key="user_name_input"    }    """Get geographic data based on IP address"""

        )

        </style>    try:

        if user_name and user_name != st.session_state.user_name:

            # Generate consistent user_id from name""", unsafe_allow_html=True)        # Using ipapi.co for geolocation (free tier)

            st.session_state.user_name = user_name

            st.session_state.user_id = hashlib.md5(user_name.encode()).hexdigest()[:16]        response = requests.get('https://ipapi.co/json/', timeout=2)

            st.success(f"✅ Logged in as: {user_name}")

            st.rerun()# ============================================        if response.status_code == 200:

        

        if st.session_state.user_id:# SESSION STATE INITIALIZATION            data = response.json()

            st.info(f"**User:** {st.session_state.user_name}\n\n**ID:** `{st.session_state.user_id[:8]}...`")

        else:# ============================================            return {

            st.warning("⚠️ Please enter your name to start using Lumiere.")

            st.stop()def initialize_session_state():                "country": data.get("country_name", "Unknown"),

        

        st.divider()    """Initialize all session state variables"""                "country_code": data.get("country_code", "Unknown"),

        

        # ===== MODE SELECTION =====                    "city": data.get("city", "Unknown"),

        st.subheader("🎯 Lumiere Mode")

            # Generate session ID (new for each browser session)                "region": data.get("region", "Unknown"),

        mode_options = {

            "all_in": "🌐 All-In Mode",    if "session_id" not in st.session_state:                "timezone": data.get("timezone", "Unknown"),

            "chat_rag": "📚 Docs & Chat Mode",

            "data_analyst": "📊 Data Analytics Mode"        st.session_state.session_id = str(uuid.uuid4())                "ip": data.get("ip", "Unknown")

        }

                        }

        lumiere_mode = st.radio(

            "Select mode:",    # User ID will be set after user enters name    except Exception as e:

            options=list(mode_options.keys()),

            format_func=lambda x: mode_options[x],    if "user_id" not in st.session_state:        print(f"Geo lookup failed: {e}")

            index=list(mode_options.keys()).index(st.session_state.lumiere_mode),

            key="mode_selector"        st.session_state.user_id = None    return {

        )

                    "country": "Unknown",

        if lumiere_mode != st.session_state.lumiere_mode:

            st.session_state.lumiere_mode = lumiere_mode    # User name input        "country_code": "Unknown", 

            st.rerun()

            if "user_name" not in st.session_state:        "city": "Unknown",

        # Mode descriptions

        mode_descriptions = {        st.session_state.user_name = ""        "region": "Unknown",

            "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",

            "chat_rag": "Chat about your uploaded documents only. No SQL or general knowledge.",            "timezone": "Unknown",

            "data_analyst": "Query CSV data with SQL and automatic visualizations. No general chat."

        }    # Chat messages        "ip": "Unknown"

        

        st.caption(f"ℹ️ {mode_descriptions[lumiere_mode]}")    if "messages" not in st.session_state:    }

        

        st.divider()        st.session_state.messages = []

        

        # ===== WORKFLOW TOGGLE =====    # ---------------------------

        st.subheader("⚙️ Settings")

            # Lumiere mode# Persistent User Identity (Cookie-Based or Session-Based)

        show_workflow = st.checkbox(

            "🔄 Show Agent Workflow",    if "lumiere_mode" not in st.session_state:# ---------------------------

            value=st.session_state.show_workflow,

            help="Display agent execution steps in real-time"        st.session_state.lumiere_mode = "all_in"# Get or create persistent user_id from cookie (if available) or use session-based ID

        )

            if "user_id" not in st.session_state:

        if show_workflow != st.session_state.show_workflow:

            st.session_state.show_workflow = show_workflow    # Workflow visibility toggle    cookies_need_save = False

        

        st.divider()    if "show_workflow" not in st.session_state:    

        

        # ===== QUICK UPLOAD =====        st.session_state.show_workflow = False    if cookies_ready:

        st.subheader("📤 Quick Upload")

                    # Cookies are available - use persistent ID

        with st.expander("Upload PDF", expanded=False):

            uploaded_pdf = st.file_uploader(    # Graph instance (built once per session)        if "persistent_user_id" not in cookies or not cookies.get("persistent_user_id"):

                "Choose a PDF file",

                type=['pdf'],    if "graph" not in st.session_state:            # First-time visitor: Create new permanent ID

                key="quick_pdf_upload",

                help="Upload a PDF to add to your knowledge base"        st.session_state.graph = build_graph()            new_user_id = str(uuid.uuid4())

            )

                        cookies["persistent_user_id"] = new_user_id

            if uploaded_pdf:

                if st.button("📄 Process PDF", key="process_pdf_btn"):# ============================================            cookies["first_visit"] = datetime.now().isoformat()

                    with st.spinner("Processing PDF..."):

                        result = process_and_store_pdf(# SIDEBAR RENDERING            cookies["session_count"] = "1"

                            file=uploaded_pdf,

                            filename=uploaded_pdf.name,# ============================================            persistent_user_id = new_user_id

                            user_id=st.session_state.user_id

                        )def render_sidebar():            is_new_user = True

                        

                        if result["success"]:    """Render the sidebar with user info, mode selection, and document stats"""            cookies_need_save = True

                            st.success(f"✅ Stored {result['chunks_stored']} chunks!")

                            st.rerun()            else:

                        else:

                            st.error(f"❌ Error: {result['error']}")    with st.sidebar:            # Returning visitor: Use existing ID from cookie

        

        with st.expander("Upload CSV", expanded=False):        st.title("💡 Lumiere")            persistent_user_id = cookies["persistent_user_id"]

            uploaded_csv = st.file_uploader(

                "Choose a CSV file",        st.caption("AI Knowledge Workspace")            is_new_user = False

                type=['csv'],

                key="quick_csv_upload",            else:

                help="Upload a CSV to store in database"

            )        st.divider()        # Cookies not available - use session-based ID (temporary)

            

            if uploaded_csv:                persistent_user_id = str(uuid.uuid4())

                table_name = st.text_input(

                    "Table name:",        # ===== USER IDENTIFICATION =====        is_new_user = True

                    value=sanitize_table_name(uploaded_csv.name),

                    key="quick_csv_table_name"        st.subheader("👤 User Identity")        print("Warning: Cookies not available, using session-based user ID")

                )

                            

                if st.button("📊 Store CSV", key="process_csv_btn"):

                    with st.spinner("Processing CSV..."):        user_name = st.text_input(    # Store persistent user_id in session_state (this is what your app uses)

                        result = process_and_store_csv(

                            file=uploaded_csv,            "Enter your name/ID:",    st.session_state.user_id = persistent_user_id

                            filename=uploaded_csv.name,

                            table_name=table_name,            value=st.session_state.user_name,    st.session_state.is_new_user = is_new_user

                            if_exists='fail',

                            user_id=st.session_state.user_id            placeholder="e.g., john_doe",    st.session_state.cookies_need_save = cookies_need_save

                        )

                                    help="Your data is stored per user. Use the same name to access your documents.",else:

                        if result["success"]:

                            st.success(f"✅ Stored {result['rows']} rows!")            key="user_name_input"    # User ID already in session state

                            st.rerun()

                        else:        )    persistent_user_id = st.session_state.user_id

                            st.error(f"❌ Error: {result['error']}")

                    is_new_user = st.session_state.get("is_new_user", False)

        st.caption("💡 For full document management, visit the [📚 Documents](/Documents) page.")

                if user_name and user_name != st.session_state.user_name:

        st.divider()

                    # Generate consistent user_id from name# ---------------------------

        # ===== DOCUMENT STATS =====

        st.subheader("📊 Your Data")            st.session_state.user_name = user_name# Session Tracking (Analytics - New Each Refresh)

        

        # Get document count            st.session_state.user_id = hashlib.md5(user_name.encode()).hexdigest()[:16]# ---------------------------

        try:

            documents = list_uploaded_documents(user_id=st.session_state.user_id)            st.success(f"✅ Logged in as: {user_name}")# Initialize session tracking

            doc_count = len(documents)

        except Exception:            st.rerun()if "session_id" not in st.session_state:

            doc_count = 0

            documents = []            # Generate new session ID for this page load (for analytics)

        

        # Get table count        if st.session_state.user_id:    st.session_state.session_id = str(uuid.uuid4())

        try:

            tables = list_all_tables(user_id=st.session_state.user_id)            st.info(f"**User:** {st.session_state.user_name}\n\n**ID:** `{st.session_state.user_id[:8]}...`")    st.session_state.session_start = datetime.now()

            table_count = len(tables)

        except Exception:        else:    st.session_state.session_start_iso = datetime.now().isoformat()

            table_count = 0

            tables = []            st.warning("⚠️ Please enter your name to start using Lumiere.")    

        

        col1, col2 = st.columns(2)            st.stop()    # Track session count for this user (only for returning users with cookies)

        with col1:

            st.metric("📄 Documents", doc_count)            if cookies_ready and not is_new_user:

        with col2:

            st.metric("📊 Tables", table_count)        st.divider()        session_count = int(cookies.get("session_count", "0")) + 1

        

        # Show document list                cookies["session_count"] = str(session_count)

        if doc_count > 0:

            with st.expander(f"📄 Documents ({doc_count})", expanded=False):        # ===== MODE SELECTION =====        st.session_state.cookies_need_save = True

                for doc in documents[:5]:

                    st.caption(f"• {doc['filename'][:30]}{'...' if len(doc['filename']) > 30 else ''}")        st.subheader("🎯 Lumiere Mode")    

                if doc_count > 5:

                    st.caption(f"... and {doc_count - 5} more")            # Get geographic data

        

        # Show table list        mode_options = {    geo_data = get_geo_data()

        if table_count > 0:

            with st.expander(f"📊 Tables ({table_count})", expanded=False):            "all_in": "🌐 All-In Mode",    

                for table in tables[:5]:

                    st.caption(f"• {table['table_name']}")            "chat_rag": "📚 Docs & Chat Mode",    # Initialize feature usage tracking

                if table_count > 5:

                    st.caption(f"... and {table_count - 5} more")            "data_analyst": "📊 Data Analytics Mode"    st.session_state.feature_usage = {

        

        st.divider()        }        "rag_queries": 0,

        

        # ===== SESSION STATS =====                "sql_queries": 0,

        st.subheader("📈 Session Stats")

                lumiere_mode = st.radio(        "visualizations": 0,

        col1, col2 = st.columns(2)

        with col1:            "Select mode:",        "documents_uploaded": 0,

            st.metric("💬 Messages", len(st.session_state.messages))

        with col2:            options=list(mode_options.keys()),        "tables_uploaded": 0,

            # Count memory items

            try:            format_func=lambda x: mode_options[x],        "feedbacks_given": 0

                memory_items = get_session_memory(st.session_state.session_id)

                memory_count = len([m for m in memory_items if m["type"] != "conversation"])            index=list(mode_options.keys()).index(st.session_state.lumiere_mode),    }

            except Exception:

                memory_count = 0            key="mode_selector"    

            st.metric("🧠 Memories", memory_count)

                )    # Initialize error tracking

        st.divider()

                    st.session_state.error_tracking = {

        # ===== ACTIONS =====

        st.subheader("🔧 Actions")        if lumiere_mode != st.session_state.lumiere_mode:        "total_errors": 0,

        

        if st.button("🗑️ Clear Chat History", use_container_width=True):            st.session_state.lumiere_mode = lumiere_mode        "error_types": {},

            st.session_state.messages = []

            clear_session_memory(st.session_state.session_id)            st.rerun()        "last_error": None

            st.success("Chat cleared!")

            st.rerun()            }

        

        if st.button("🔄 New Session", use_container_width=True):        # Mode descriptions    

            # Generate new session ID but keep user_id

            st.session_state.session_id = str(uuid.uuid4())        mode_descriptions = {    # Capture user metadata

            st.session_state.messages = []

            st.success("New session started!")            "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",    st.session_state.user_metadata = {

            st.rerun()

                    "chat_rag": "Chat about your uploaded documents only. No SQL or general knowledge.",        "first_visit": datetime.now().isoformat(),

        st.divider()

                    "data_analyst": "Query CSV data with SQL and automatic visualizations. No general chat."        "user_agent": st.context.headers.get("User-Agent", "Unknown") if hasattr(st, 'context') and hasattr(st.context, 'headers') else "Unknown",

        # ===== FOOTER =====

        st.caption("🔍 **Observability:** Langfuse enabled")        }        "platform": platform.system(),

        st.caption(f"🆔 **Session:** `{st.session_state.session_id[:8]}...`")

                "session_count": 1,

# ============================================

# VISUALIZATION RENDERING        st.caption(f"ℹ️ {mode_descriptions[lumiere_mode]}")        "country": geo_data["country"],

# ============================================

def render_visualization(viz_config: dict, sql_results: dict):                "country_code": geo_data["country_code"],

    """Render chart based on visualization configuration"""

            st.divider()        "city": geo_data["city"],

    if not viz_config or not sql_results:

        return                "region": geo_data["region"],

    

    chart_type = viz_config.get("chart_type")        # ===== WORKFLOW TOGGLE =====        "timezone": geo_data["timezone"],

    x_column = viz_config.get("x_column")

    y_column = viz_config.get("y_column")        st.subheader("⚙️ Settings")        "ip": geo_data["ip"]

    title = viz_config.get("title", "Data Visualization")

                }

    data = sql_results.get("data", [])

            show_workflow = st.checkbox(

    if not data or not chart_type:

        return            "🔄 Show Agent Workflow",# Always initialize tracking dicts if not exist

    

    try:            value=st.session_state.show_workflow,if "feature_usage" not in st.session_state:

        # Convert data to dict format for Plotly

        if hasattr(data[0], 'keys'):            help="Display agent execution steps in real-time"    st.session_state.feature_usage = {

            # Row objects

            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}        )        "rag_queries": 0,

        elif isinstance(data[0], dict):

            # Already dicts                "sql_queries": 0,

            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}

        else:        if show_workflow != st.session_state.show_workflow:        "visualizations": 0,

            st.warning("Cannot render visualization: unsupported data format")

            return            st.session_state.show_workflow = show_workflow        "documents_uploaded": 0,

        

        # Create appropriate chart                "tables_uploaded": 0,

        if chart_type == "bar":

            fig = go.Figure(data=[        st.divider()        "feedbacks_given": 0

                go.Bar(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []))

            ])            }

            fig.update_layout(

                title=title,        # ===== QUICK UPLOAD =====

                xaxis_title=x_column,

                yaxis_title=y_column,        st.subheader("📤 Quick Upload")if "error_tracking" not in st.session_state:

                template="plotly_white"

            )            st.session_state.error_tracking = {

            st.plotly_chart(fig, use_container_width=True)

                with st.expander("Upload PDF", expanded=False):        "total_errors": 0,

        elif chart_type == "line":

            fig = go.Figure(data=[            uploaded_pdf = st.file_uploader(        "error_types": {},

                go.Scatter(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []), mode='lines+markers')

            ])                "Choose a PDF file",        "last_error": None

            fig.update_layout(

                title=title,                type=['pdf'],    }

                xaxis_title=x_column,

                yaxis_title=y_column,                key="quick_pdf_upload",

                template="plotly_white"

            )                help="Upload a PDF to add to your knowledge base"# Calculate session duration

            st.plotly_chart(fig, use_container_width=True)

                    )session_duration_seconds = (datetime.now() - st.session_state.session_start).total_seconds()

        elif chart_type == "pie":

            fig = go.Figure(data=[            session_duration_minutes = round(session_duration_seconds / 60, 2)

                go.Pie(labels=data_dict.get(x_column, []), values=data_dict.get(y_column, []))

            ])            if uploaded_pdf:

            fig.update_layout(title=title, template="plotly_white")

            st.plotly_chart(fig, use_container_width=True)                if st.button("📄 Process PDF", key="process_pdf_btn"):# Store user_id and metadata in environment for Langfuse tracking

        

        elif chart_type == "scatter":                    with st.spinner("Processing PDF..."):os.environ["LANGFUSE_USER_ID"] = st.session_state.user_id

            fig = go.Figure(data=[

                go.Scatter(x=data_dict.get(x_column, []), y=data_dict.get(y_column, []), mode='markers')                        result = process_and_store_pdf(

            ])

            fig.update_layout(                            file=uploaded_pdf,# Store comprehensive metadata as JSON for Langfuse

                title=title,

                xaxis_title=x_column,                            filename=uploaded_pdf.name,if "user_metadata" in st.session_state:

                yaxis_title=y_column,

                template="plotly_white"                            user_id=st.session_state.user_id    comprehensive_metadata = {

            )

            st.plotly_chart(fig, use_container_width=True)                        )        **st.session_state.user_metadata,

        

        elif chart_type == "histogram":                                "session_duration_minutes": session_duration_minutes,

            fig = go.Figure(data=[

                go.Histogram(x=data_dict.get(x_column, []))                        if result["success"]:        "feature_usage": st.session_state.feature_usage,

            ])

            fig.update_layout(                            st.success(f"✅ Stored {result['chunks_stored']} chunks!")        "error_tracking": {

                title=title,

                xaxis_title=x_column,                            st.rerun()            "total_errors": st.session_state.error_tracking["total_errors"],

                yaxis_title="Count",

                template="plotly_white"                        else:            "error_types": list(st.session_state.error_tracking["error_types"].keys())

            )

            st.plotly_chart(fig, use_container_width=True)                            st.error(f"❌ Error: {result['error']}")        }

        

        elif chart_type == "table":            }

            # Just show the data as table

            import pandas as pd        with st.expander("Upload CSV", expanded=False):    os.environ["LANGFUSE_USER_METADATA"] = json.dumps(comprehensive_metadata)

            df = pd.DataFrame(data_dict)

            st.dataframe(df, use_container_width=True)            uploaded_csv = st.file_uploader(

        

        else:                "Choose a CSV file",# ---------------------------

            st.info(f"Chart type '{chart_type}' not supported yet.")

                    type=['csv'],# Apple-like Custom CSS

    except Exception as e:

        st.error(f"Error rendering visualization: {e}")                key="quick_csv_upload",# ---------------------------



# ============================================                help="Upload a CSV to store in database"st.markdown("""

# GRAPH INVOCATION

# ============================================            )<style>

def invoke_graph(user_message: str):

    """Invoke the LangGraph workflow with proper state management"""                /* Apple-inspired color palette and typography */

    

    # Create Langfuse trace            if uploaded_csv:    :root {

    trace = langfuse.trace(

        name="lumiere_chat",                table_name = st.text_input(        --apple-blue: #007AFF;

        user_id=st.session_state.user_id,

        session_id=st.session_state.session_id,                    "Table name:",        --apple-green: #34C759;

        input={"message": user_message, "mode": st.session_state.lumiere_mode},

        metadata={                    value=sanitize_table_name(uploaded_csv.name),        --apple-gray: #86868B;

            "lumiere_mode": st.session_state.lumiere_mode,

            "message_count": len(st.session_state.messages),                    key="quick_csv_table_name"        --apple-dark: #1D1D1F;

            "timestamp": datetime.now().isoformat()

        }                )        --apple-bg: #F5F5F7;

    )

                        }

    try:

        # Build initial state                if st.button("📊 Store CSV", key="process_csv_btn"):    

        initial_state: AgentState = {

            "messages": [user_message],                    with st.spinner("Processing CSV..."):    /* Main container styling */

            "session_id": st.session_state.session_id,

            "user_id": st.session_state.user_id,                        result = process_and_store_csv(    .main {

            "lumiere_mode": st.session_state.lumiere_mode,

            "question": user_message,                            file=uploaded_csv,        background-color: var(--apple-bg);

            "user_input": user_message,

            "intent": None,                            filename=uploaded_csv.name,    }

            "needs_rag": False,

            "needs_sql": False,                            table_name=table_name,    

            "retrieved_docs": [],

            "sql_query": None,                            if_exists='fail',    /* Header styling */

            "sql_results": None,

            "visualization_config": None,                            user_id=st.session_state.user_id    h1 {

            "answer": None,

            "retry_count": 0,                        )        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

            "decision": None,

            "reasoning_mode": None,                                font-weight: 600;

            "memory_signal": None,

        }                        if result["success"]:        color: var(--apple-dark);

        

        # Invoke graph with workflow display                            st.success(f"✅ Stored {result['rows']} rows!")        letter-spacing: -0.5px;

        if st.session_state.show_workflow:

            with st.status("🤖 Processing your request...", expanded=True) as status:                            st.rerun()    }

                st.write("🎯 Classifying intent...")

                                        else:    

                # Stream graph execution

                final_state = None                            st.error(f"❌ Error: {result['error']}")    /* Subtitle styling */

                for state in st.session_state.graph.stream(initial_state):

                    # Update status based on state            .subtitle {

                    if "intent" in state and state.get("intent"):

                        intent = state.get("intent")        st.caption("💡 For full document management, visit the [📚 Documents](/Documents) page.")        color: var(--apple-gray);

                        st.write(f"📋 Intent detected: **{intent}**")

                                    font-size: 1.1rem;

                    if state.get("needs_rag"):

                        st.write("📚 Retrieving documents...")        st.divider()        font-weight: 400;

                    

                    if state.get("needs_sql"):                margin-top: -1rem;

                        st.write("🗄️ Executing SQL query...")

                            # ===== DOCUMENT STATS =====        margin-bottom: 2rem;

                    if state.get("retrieved_docs"):

                        doc_count = len(state.get("retrieved_docs", []))        st.subheader("📊 Your Data")    }

                        st.write(f"📄 Retrieved {doc_count} documents")

                                

                    if state.get("sql_results"):

                        sql_success = state.get("sql_results", {}).get("success", False)        # Get document count    /* Feature badges */

                        if sql_success:

                            row_count = state.get("sql_results", {}).get("row_count", 0)        try:    .feature-badge {

                            st.write(f"✅ SQL query returned {row_count} rows")

                        else:            documents = list_uploaded_documents(user_id=st.session_state.user_id)        display: inline-block;

                            st.write("❌ SQL query failed")

                                doc_count = len(documents)        padding: 0.3rem 0.8rem;

                    if state.get("answer"):

                        st.write("💭 Generating response...")        except Exception:        margin: 0.2rem;

                    

                    if state.get("visualization_config"):            doc_count = 0        background: linear-gradient(135deg, var(--apple-blue) 0%, #0051D5 100%);

                        st.write("📊 Creating visualization...")

                                documents = []        color: white;

                    final_state = state

                                border-radius: 12px;

                status.update(label="✅ Processing complete!", state="complete")

        else:        # Get table count        font-size: 0.85rem;

            # Execute without workflow display

            final_state = None        try:        font-weight: 500;

            for state in st.session_state.graph.stream(initial_state):

                final_state = state            tables = list_all_tables(user_id=st.session_state.user_id)        box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);

        

        # Extract answer and metadata            table_count = len(tables)    }

        answer = final_state.get("answer", "I couldn't generate a response.")

        sql_results = final_state.get("sql_results")        except Exception:    

        visualization_config = final_state.get("visualization_config")

        memory_signal = final_state.get("memory_signal")            table_count = 0    /* Cards with shadow */

        

        # Store conversation in session memory            tables = []    .card {

        append_session_memory(

            st.session_state.session_id,                background: white;

            {

                "type": "conversation",        col1, col2 = st.columns(2)        border-radius: 12px;

                "content": f"User: {user_message}",

                "turn": len(st.session_state.messages) // 2        with col1:        padding: 1.5rem;

            }

        )            st.metric("📄 Documents", doc_count)        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

        

        append_session_memory(        with col2:        margin: 1rem 0;

            st.session_state.session_id,

            {            st.metric("📊 Tables", table_count)    }

                "type": "conversation",

                "content": f"Assistant: {answer}",            

                "turn": len(st.session_state.messages) // 2

            }        # Show document list    /* Sidebar styling */

        )

                if doc_count > 0:    section[data-testid="stSidebar"] {

        # Store memory signal if detected

        if memory_signal:            with st.expander(f"📄 Documents ({doc_count})", expanded=False):        background-color: #E8E8E8 !important;

            append_session_memory(

                st.session_state.session_id,                for doc in documents[:5]:        border-right: 1px solid #D1D1D6;

                memory_signal

            )                    st.caption(f"• {doc['filename'][:30]}{'...' if len(doc['filename']) > 30 else ''}")    }

            

            # Also store in semantic memory for long-term recall                if doc_count > 5:    

            try:

                store_memory(                    st.caption(f"... and {doc_count - 5} more")    /* Sidebar text - all black */

                    content=memory_signal["content"],

                    memory_type=memory_signal["type"],            section[data-testid="stSidebar"] .stMarkdown,

                    user_id=st.session_state.user_id,

                    session_id=st.session_state.session_id,        # Show table list    section[data-testid="stSidebar"] .stMarkdown p,

                    metadata={

                        "timestamp": datetime.now().isoformat(),        if table_count > 0:    section[data-testid="stSidebar"] .stMarkdown h1,

                        "lumiere_mode": st.session_state.lumiere_mode

                    }            with st.expander(f"📊 Tables ({table_count})", expanded=False):    section[data-testid="stSidebar"] .stMarkdown h2,

                )

            except Exception as e:                for table in tables[:5]:    section[data-testid="stSidebar"] .stMarkdown h3,

                print(f"Warning: Failed to store semantic memory: {e}")

                            st.caption(f"• {table['table_name']}")    section[data-testid="stSidebar"] .stMarkdown strong,

        # Update trace

        trace.update(                if table_count > 5:    section[data-testid="stSidebar"] label,

            output={

                "answer": answer,                    st.caption(f"... and {table_count - 5} more")    section[data-testid="stSidebar"] p,

                "has_sql": bool(sql_results),

                "has_visualization": bool(visualization_config),            section[data-testid="stSidebar"] h1,

                "memory_signal": memory_signal

            }        st.divider()    section[data-testid="stSidebar"] h2,

        )

                    section[data-testid="stSidebar"] h3,

        return {

            "answer": answer,        # ===== SESSION STATS =====    section[data-testid="stSidebar"] span,

            "sql_results": sql_results,

            "visualization_config": visualization_config        st.subheader("📈 Session Stats")    section[data-testid="stSidebar"] div {

        }

                    color: #000000 !important;

    except Exception as e:

        trace.update(        col1, col2 = st.columns(2)    }

            output={"error": str(e)},

            level="ERROR"        with col1:    

        )

        st.error(f"❌ Error processing request: {e}")            st.metric("💬 Messages", len(st.session_state.messages))    /* Sidebar checkbox labels */

        return {

            "answer": f"I encountered an error: {str(e)}",        with col2:    section[data-testid="stSidebar"] .stCheckbox label {

            "sql_results": None,

            "visualization_config": None            # Count memory items        color: #000000 !important;

        }

    finally:            try:    }

        trace.end()

                memory_items = get_session_memory(st.session_state.session_id)    

# ============================================

# MAIN CHAT INTERFACE                memory_count = len([m for m in memory_items if m["type"] != "conversation"])    /* Sidebar selectbox */

# ============================================

def render_chat_interface():            except Exception:    section[data-testid="stSidebar"] .stSelectbox label,

    """Render the main chat interface"""

                    memory_count = 0    section[data-testid="stSidebar"] .stSelectbox div {

    # Show mode badge

    mode_classes = {            st.metric("🧠 Memories", memory_count)        color: #000000 !important;

        "all_in": "mode-all-in",

        "chat_rag": "mode-chat-rag",            }

        "data_analyst": "mode-data-analyst"

    }        st.divider()    

    

    mode_names = {            /* Sidebar caption text */

        "all_in": "🌐 All-In Mode",

        "chat_rag": "📚 Docs & Chat Mode",        # ===== ACTIONS =====    section[data-testid="stSidebar"] .stCaption {

        "data_analyst": "📊 Data Analytics Mode"

    }        st.subheader("🔧 Actions")        color: #000000 !important;

    

    st.markdown(            }

        f'<div class="mode-badge {mode_classes[st.session_state.lumiere_mode]}">'

        f'{mode_names[st.session_state.lumiere_mode]}'        if st.button("🗑️ Clear Chat History", use_container_width=True):    

        f'</div>',

        unsafe_allow_html=True            st.session_state.messages = []    /* Sidebar button text */

    )

                clear_session_memory(st.session_state.session_id)    section[data-testid="stSidebar"] button {

    # Welcome message for new users

    if len(st.session_state.messages) == 0:            st.success("Chat cleared!")        color: #000000 !important;

        st.info(f"""

        👋 **Welcome to Lumiere!**            st.rerun()    }

        

        **Getting Started:**            

        1. ✅ You're logged in as **{st.session_state.user_name}**

        2. 📁 Upload documents in the sidebar or visit the [📚 Documents](/Documents) page        if st.button("🔄 New Session", use_container_width=True):    /* Sidebar metrics */

        3. 💬 Start chatting below!

                    # Generate new session ID but keep user_id    section[data-testid="stSidebar"] [data-testid="stMetric"] {

        **Current Mode:** {mode_names[st.session_state.lumiere_mode]}

        - {({            st.session_state.session_id = str(uuid.uuid4())        background: transparent;

            "all_in": "Full AI capabilities: RAG, SQL, general knowledge, and visualizations.",

            "chat_rag": "Chat about your uploaded documents only.",            st.session_state.messages = []        color: #000000 !important;

            "data_analyst": "Query CSV data with SQL and automatic visualizations."

        })[st.session_state.lumiere_mode]}            st.success("New session started!")    }

        

        **Tips:**            st.rerun()    

        - Upload PDFs to ask questions about your documents

        - Upload CSVs to query data with natural language            section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {

        - Switch modes in the sidebar for different capabilities

        """)        st.divider()        color: #000000 !important;

    

    # Display chat messages            }

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):        # ===== FOOTER =====    

            st.markdown(message["content"])

                    st.caption("🔍 **Observability:** Langfuse enabled")    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {

            # Show visualization if present

            if message["role"] == "assistant" and "visualization" in message:        st.caption(f"🆔 **Session:** `{st.session_state.session_id[:8]}...`")        color: #000000 !important;

                render_visualization(

                    message["visualization"],    }

                    message.get("sql_results")

                )# ============================================    

    

    # Chat input# VISUALIZATION RENDERING    /* Button styling */

    if prompt := st.chat_input("Ask me anything..."):

        # Add user message to chat# ============================================    .stButton > button {

        st.session_state.messages.append({"role": "user", "content": prompt})

        def render_visualization(viz_config: dict, sql_results: dict):        border-radius: 10px;

        with st.chat_message("user"):

            st.markdown(prompt)    """Render chart based on visualization configuration"""        font-weight: 500;

        

        # Generate response            transition: all 0.2s ease;

        with st.chat_message("assistant"):

            response = invoke_graph(prompt)    if not viz_config or not sql_results:        border: none;

            

            # Display answer        return        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

            st.markdown(response["answer"])

                    }

            # Display visualization if present

            if response["visualization_config"] and st.session_state.lumiere_mode == "data_analyst":    chart_type = viz_config.get("chart_type")    

                render_visualization(

                    response["visualization_config"],    x_column = viz_config.get("x_column")    .stButton > button:hover {

                    response["sql_results"]

                )    y_column = viz_config.get("y_column")        transform: translateY(-1px);

        

        # Add assistant message to chat    title = viz_config.get("title", "Data Visualization")        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

        assistant_message = {

            "role": "assistant",        }

            "content": response["answer"]

        }    data = sql_results.get("data", [])    

        

        if response["visualization_config"]:        /* Metrics styling */

            assistant_message["visualization"] = response["visualization_config"]

            assistant_message["sql_results"] = response["sql_results"]    if not data or not chart_type:    [data-testid="stMetric"] {

        

        st.session_state.messages.append(assistant_message)        return        background: white;

        

        st.rerun()            padding: 1rem;



# ============================================    try:        border-radius: 10px;

# MAIN APPLICATION

# ============================================        # Convert data to dict format for Plotly        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

def main():

    """Main application entry point"""        if hasattr(data[0], 'keys'):    }

    

    # Initialize session state            # Row objects    

    initialize_session_state()

                data_dict = {col: [row[col] for row in data] for col in data[0].keys()}    /* Clean expander */

    # Render sidebar

    render_sidebar()        elif isinstance(data[0], dict):    .streamlit-expanderHeader {

    

    # Main content area            # Already dicts        background-color: white;

    st.title("💡 Lumiere")

    st.caption("AI Knowledge Workspace - Multi-Agent RAG System")            data_dict = {col: [row[col] for row in data] for col in data[0].keys()}        border-radius: 8px;

    

    # Render chat interface        else:        font-weight: 500;

    render_chat_interface()

            st.warning("Cannot render visualization: unsupported data format")    }

if __name__ == "__main__":

    main()            return    


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
