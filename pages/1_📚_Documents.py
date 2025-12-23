"""
Document Management Page
Upload and manage PDFs and CSV files
"""
import streamlit as st
from rag.pdf_processor import (
    process_and_store_pdf,
    list_uploaded_documents,
    delete_document
)
from database.csv_processor import (
    process_and_store_csv,
    list_all_tables,
    get_table_preview,
    sanitize_table_name
)
from database.sqlite_client import client as db_client

st.set_page_config(page_title="Document Management - Lumiere", layout="wide")

st.title("📚 Document Management")
st.caption("Upload and manage your knowledge base")

# Create tabs for different document types
tab1, tab2 = st.tabs(["📄 PDF Documents", "📊 CSV Data"])

# ============================================
# PDF TAB
# ============================================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Upload PDF")
        
        uploaded_pdf = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF document to add to the knowledge base",
            key="pdf_uploader"
        )
        
        if uploaded_pdf:
            st.info(f"**File:** {uploaded_pdf.name}")
            st.info(f"**Size:** {uploaded_pdf.size / 1024:.1f} KB")
            
            # Get user ID from session
            user_id = st.session_state.get("user_id", "default_user")
            
            if st.button("Process & Store PDF", type="primary"):
                with st.spinner("Processing PDF..."):
                    # Process the PDF
                    result = process_and_store_pdf(
                        file=uploaded_pdf,
                        filename=uploaded_pdf.name,
                        user_id=user_id
                    )
                    
                    if result["success"]:
                        st.success("✅ PDF processed successfully!")
                        st.json({
                            "Document ID": result["doc_id"],
                            "Chunks Created": result["chunks_stored"],
                            "Text Length": result["text_length"],
                            "Timestamp": result["upload_timestamp"]
                        })
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['error']}")
    
    with col2:
        st.subheader("Uploaded Documents")
        
        # Get user ID
        user_id = st.session_state.get("user_id", "default_user")
        
        # List documents
        documents = list_uploaded_documents(user_id=user_id)
        
        if documents:
            st.write(f"**Total Documents:** {len(documents)}")
            
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}", expanded=False):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.markdown(f"""
                        - **Document ID:** `{doc['doc_id'][:16]}...`
                        - **Uploaded:** {doc['upload_timestamp'][:19]}
                        - **Chunks:** {doc['total_chunks']}
                        - **Text Length:** {doc['text_length']} chars
                        """)
                    
                    with col_b:
                        if st.button("🗑️ Delete", key=f"del_{doc['doc_id']}"):
                            result = delete_document(doc['doc_id'])
                            if result["success"]:
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error(result["error"])
        else:
            st.info("No documents uploaded yet. Upload a PDF to get started!")

# ============================================
# CSV TAB
# ============================================
with tab2:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Upload CSV")
        
        uploaded_csv = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file to store in database",
            key="csv_uploader"
        )
        
        if uploaded_csv:
            st.info(f"**File:** {uploaded_csv.name}")
            st.info(f"**Size:** {uploaded_csv.size / 1024:.1f} KB")
            
            # Preview CSV
            import pandas as pd
            try:
                df_preview = pd.read_csv(uploaded_csv)
                uploaded_csv.seek(0)  # Reset file pointer
                
                st.write("**Preview (first 5 rows):**")
                st.dataframe(df_preview.head(), use_container_width=True)
                
                # Table name input
                default_table_name = sanitize_table_name(uploaded_csv.name)
                table_name = st.text_input(
                    "Table Name",
                    value=default_table_name,
                    help="Name for the database table"
                )
                
                # If exists option
                if_exists = st.radio(
                    "If table exists:",
                    options=['fail', 'replace', 'append'],
                    help="fail: Show error | replace: Drop and recreate | append: Add to existing"
                )
                
                # Get user ID from session
                user_id = st.session_state.get("user_id", "default_user")
                
                if st.button("Store to Database", type="primary"):
                    with st.spinner("Processing CSV..."):
                        # Process the CSV
                        result = process_and_store_csv(
                            file=uploaded_csv,
                            filename=uploaded_csv.name,
                            table_name=table_name,
                            if_exists=if_exists,
                            user_id=user_id
                        )
                        
                        if result["success"]:
                            st.success("✅ CSV stored successfully!")
                            st.json({
                                "Table Name": result["table_name"],
                                "Rows": result["rows"],
                                "Columns": result["columns"],
                                "Timestamp": result["upload_timestamp"]
                            })
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result['error']}")
            
            except Exception as e:
                st.error(f"Error previewing CSV: {e}")
    
    with col2:
        st.subheader("Database Tables")
        
        # Get user_id from session state
        user_id = st.session_state.get("user_id", "default_user")
        
        # List tables
        tables = list_all_tables(user_id=user_id)
        
        if tables:
            st.write(f"**Total Tables:** {len(tables)}")
            
            for table in tables:
                with st.expander(f"📊 {table['table_name']}", expanded=False):
                    st.markdown(f"""
                    - **Rows:** {table['row_count']}
                    - **Columns:** {table['column_count']}
                    - **Column Names:** {', '.join(table['columns'][:10])}{'...' if len(table['columns']) > 10 else ''}
                    """)
                    
                    # Show preview
                    if st.button("👁️ View Preview", key=f"preview_{table['table_name']}"):
                        preview = get_table_preview(table['table_name'], user_id=user_id, limit=10)
                        if preview["success"]:
                            st.write("**Sample Data:**")
                            st.dataframe(preview["preview_rows"], use_container_width=True)
                    
                    # Delete button
                    if st.button("🗑️ Delete Table", key=f"del_{table['table_name']}"):
                        try:
                            table_name = table['table_name']
                            print(f"Attempting to delete table: {table_name}")
                            
                            if db_client.drop_table(table_name):
                                st.success(f"Successfully deleted table: {table_name}")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete table: {table_name}")
                        except Exception as e:
                            st.error(f"Error deleting table: {str(e)}")
                            print(f"Exception in delete: {e}")
                            import traceback
                            traceback.print_exc()
        else:
            st.info("No tables in database yet. Upload a CSV to get started!")

# ============================================
# FOOTER
# ============================================
st.divider()
st.caption("💡 **Tip:** PDF files are stored in Qdrant vector database for semantic search. CSV files are stored in SQLite for structured queries.")
