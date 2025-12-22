"""
PDF processing module for extracting text and storing in vector database.
"""
import io
from typing import BinaryIO
from uuid import uuid4
from datetime import datetime

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from rag.chunking import chunk_text
from rag.embeddings import embed_text
from rag.qdrant_client import client
from config.settings import DOCUMENT_COLLECTION_NAME


def extract_text_from_pdf(file: BinaryIO, method: str = "pypdf2") -> str:
    """
    Extract text from PDF file.
    
    Args:
        file: Binary file object (e.g., from st.file_uploader)
        method: "pypdf2" or "pdfplumber" (default: pypdf2)
    
    Returns:
        Extracted text as string
    """
    if method == "pdfplumber" and pdfplumber:
        return _extract_with_pdfplumber(file)
    elif PyPDF2:
        return _extract_with_pypdf2(file)
    else:
        raise ImportError("No PDF library available. Install PyPDF2 or pdfplumber.")


def _extract_with_pypdf2(file: BinaryIO) -> str:
    """Extract text using PyPDF2."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    
    for page_num, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page_text
    
    return text.strip()


def _extract_with_pdfplumber(file: BinaryIO) -> str:
    """Extract text using pdfplumber (better for complex layouts)."""
    text = ""
    
    with pdfplumber.open(file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
    
    return text.strip()


def process_and_store_pdf(
    file: BinaryIO,
    filename: str,
    user_id: str = "default_user",
    metadata: dict = None
) -> dict:
    """
    Complete pipeline: Extract → Chunk → Embed → Store PDF in Qdrant.
    
    Args:
        file: Binary file object
        filename: Original filename
        user_id: User identifier
        metadata: Additional metadata to store
    
    Returns:
        dict with processing statistics
    """
    # Generate unique document ID
    doc_id = str(uuid4())
    upload_timestamp = datetime.now().isoformat()
    
    # Extract text
    try:
        text = extract_text_from_pdf(file)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract text: {str(e)}",
            "doc_id": doc_id
        }
    
    if not text or len(text.strip()) < 10:
        return {
            "success": False,
            "error": "No text extracted from PDF or text too short",
            "doc_id": doc_id
        }
    
    # Chunk text
    chunks = chunk_text(text)
    
    if not chunks:
        return {
            "success": False,
            "error": "No chunks generated from text",
            "doc_id": doc_id
        }
    
    # Prepare metadata
    base_metadata = {
        "doc_id": doc_id,
        "filename": filename,
        "user_id": user_id,
        "upload_timestamp": upload_timestamp,
        "document_type": "pdf",
        "total_chunks": len(chunks),
        "text_length": len(text)
    }
    
    if metadata:
        base_metadata.update(metadata)
    
    # Embed and store chunks
    points = []
    for idx, chunk in enumerate(chunks):
        try:
            vector = embed_text(chunk)
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_index": idx,
                "text": chunk
            })
            
            points.append({
                "id": str(uuid4()),
                "vector": vector,
                "payload": chunk_metadata
            })
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to embed chunk {idx}: {str(e)}",
                "doc_id": doc_id,
                "chunks_processed": idx
            }
    
    # Store in Qdrant
    try:
        client.upsert(
            collection_name=DOCUMENT_COLLECTION_NAME,
            points=points
        )
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to store in Qdrant: {str(e)}",
            "doc_id": doc_id,
            "chunks_prepared": len(points)
        }
    
    return {
        "success": True,
        "doc_id": doc_id,
        "filename": filename,
        "chunks_stored": len(points),
        "text_length": len(text),
        "upload_timestamp": upload_timestamp
    }


def list_uploaded_documents(user_id: str = None, limit: int = 100) -> list[dict]:
    """
    List all documents in the collection with metadata.
    
    Args:
        user_id: Filter by user (optional)
        limit: Maximum documents to return
    
    Returns:
        List of document metadata
    """
    try:
        # Scroll through collection to get unique documents
        scroll_result = client.scroll(
            collection_name=DOCUMENT_COLLECTION_NAME,
            limit=limit,
            with_payload=True
        )
        
        # Group by doc_id to get unique documents
        docs_by_id = {}
        for point in scroll_result[0]:
            payload = point.payload
            doc_id = payload.get("doc_id")
            
            # Filter by user if specified
            if user_id and payload.get("user_id") != user_id:
                continue
            
            if doc_id and doc_id not in docs_by_id:
                docs_by_id[doc_id] = {
                    "doc_id": doc_id,
                    "filename": payload.get("filename", "Unknown"),
                    "user_id": payload.get("user_id", "Unknown"),
                    "upload_timestamp": payload.get("upload_timestamp", "Unknown"),
                    "total_chunks": payload.get("total_chunks", 0),
                    "text_length": payload.get("text_length", 0)
                }
        
        # Sort by upload timestamp (newest first)
        documents = list(docs_by_id.values())
        documents.sort(key=lambda x: x.get("upload_timestamp", ""), reverse=True)
        
        return documents
    except Exception as e:
        return []


def delete_document(doc_id: str) -> dict:
    """
    Delete all chunks of a document from Qdrant.
    
    Args:
        doc_id: Document ID to delete
    
    Returns:
        dict with deletion status
    """
    try:
        # Delete all points with matching doc_id
        client.delete(
            collection_name=DOCUMENT_COLLECTION_NAME,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "doc_id",
                            "match": {"value": doc_id}
                        }
                    ]
                }
            }
        )
        
        return {
            "success": True,
            "doc_id": doc_id,
            "message": "Document deleted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "doc_id": doc_id,
            "error": f"Failed to delete document: {str(e)}"
        }
