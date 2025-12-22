"""
CSV processing module for parsing and storing data in SQLite.
"""
import pandas as pd
from typing import BinaryIO, Dict, Any, List
from datetime import datetime
import re

from database.sqlite_client import client as db_client


def sanitize_table_name(name: str) -> str:
    """
    Sanitize table name to be SQL-safe.
    
    Args:
        name: Original table name
    
    Returns:
        Sanitized table name
    """
    # Remove extension
    name = name.replace('.csv', '').replace('.CSV', '')
    
    # Replace spaces and special chars with underscore
    name = re.sub(r'[^\w]', '_', name)
    
    # Ensure starts with letter
    if name and not name[0].isalpha():
        name = 'table_' + name
    
    # Convert to lowercase
    name = name.lower()
    
    return name


def sanitize_column_name(name: str) -> str:
    """
    Sanitize column name to be SQL-safe.
    
    Args:
        name: Original column name
    
    Returns:
        Sanitized column name
    """
    # Replace spaces and special chars with underscore
    name = re.sub(r'[^\w]', '_', name)
    
    # Ensure starts with letter or underscore
    if name and name[0].isdigit():
        name = '_' + name
    
    # Convert to lowercase
    name = name.lower()
    
    return name


def infer_sql_type(dtype: str) -> str:
    """
    Infer SQL type from pandas dtype.
    
    Args:
        dtype: Pandas dtype string
    
    Returns:
        SQL type string
    """
    dtype = str(dtype).lower()
    
    if 'int' in dtype:
        return 'INTEGER'
    elif 'float' in dtype:
        return 'REAL'
    elif 'bool' in dtype:
        return 'INTEGER'  # Store as 0/1
    elif 'datetime' in dtype:
        return 'TEXT'  # Store as ISO format
    else:
        return 'TEXT'


def parse_csv(file: BinaryIO) -> pd.DataFrame:
    """
    Parse CSV file into pandas DataFrame.
    
    Args:
        file: Binary file object
    
    Returns:
        pandas DataFrame
    """
    try:
        # Try different encodings
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        file.seek(0)
        df = pd.read_csv(file, encoding='latin-1')
    
    # Sanitize column names
    df.columns = [sanitize_column_name(col) for col in df.columns]
    
    return df


def create_table_from_dataframe(
    df: pd.DataFrame,
    table_name: str,
    if_exists: str = 'fail'
) -> Dict[str, Any]:
    """
    Create SQLite table from pandas DataFrame.
    
    Args:
        df: pandas DataFrame
        table_name: Name for the table
        if_exists: 'fail', 'replace', or 'append'
    
    Returns:
        dict with creation status
    """
    table_name = sanitize_table_name(table_name)
    
    # Check if table exists
    if db_client.table_exists(table_name):
        if if_exists == 'fail':
            return {
                "success": False,
                "error": f"Table '{table_name}' already exists",
                "table_name": table_name
            }
        elif if_exists == 'replace':
            db_client.drop_table(table_name)
    
    # Build CREATE TABLE statement
    columns = []
    for col_name, dtype in df.dtypes.items():
        sql_type = infer_sql_type(dtype)
        columns.append(f"{col_name} {sql_type}")
    
    # Add metadata columns
    columns.append("_upload_timestamp TEXT")
    columns.append("_row_number INTEGER")
    
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {', '.join(columns)}
    )
    """
    
    try:
        db_client.execute(create_sql)
        return {
            "success": True,
            "table_name": table_name,
            "columns": len(df.columns),
            "sql_types": {col: infer_sql_type(dtype) for col, dtype in df.dtypes.items()}
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create table: {str(e)}",
            "table_name": table_name
        }


def insert_dataframe(
    df: pd.DataFrame,
    table_name: str
) -> Dict[str, Any]:
    """
    Insert DataFrame rows into SQLite table.
    
    Args:
        df: pandas DataFrame
        table_name: Target table name
    
    Returns:
        dict with insertion status
    """
    table_name = sanitize_table_name(table_name)
    upload_timestamp = datetime.now().isoformat()
    
    # Add metadata columns
    df['_upload_timestamp'] = upload_timestamp
    df['_row_number'] = range(1, len(df) + 1)
    
    # Build INSERT statement
    columns = list(df.columns)
    placeholders = ', '.join(['?' for _ in columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    try:
        conn = db_client.connect()
        cursor = conn.cursor()
        
        # Convert DataFrame to list of tuples
        rows = [tuple(row) for row in df.values]
        
        # Batch insert
        cursor.executemany(insert_sql, rows)
        conn.commit()
        
        return {
            "success": True,
            "table_name": table_name,
            "rows_inserted": len(rows),
            "upload_timestamp": upload_timestamp
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to insert data: {str(e)}",
            "table_name": table_name
        }


def process_and_store_csv(
    file: BinaryIO,
    filename: str,
    table_name: str = None,
    if_exists: str = 'fail',
    user_id: str = "default_user"
) -> Dict[str, Any]:
    """
    Complete pipeline: Parse → Create Table → Insert CSV data into SQLite.
    
    Args:
        file: Binary file object
        filename: Original filename
        table_name: Custom table name (optional, will use filename if None)
        if_exists: 'fail', 'replace', or 'append'
        user_id: User identifier
    
    Returns:
        dict with processing statistics
    """
    # Use filename as table name if not provided
    if not table_name:
        table_name = sanitize_table_name(filename)
    else:
        table_name = sanitize_table_name(table_name)
    
    # Parse CSV
    try:
        df = parse_csv(file)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse CSV: {str(e)}",
            "table_name": table_name
        }
    
    if df.empty:
        return {
            "success": False,
            "error": "CSV file is empty",
            "table_name": table_name
        }
    
    # Create table
    create_result = create_table_from_dataframe(df, table_name, if_exists)
    if not create_result["success"]:
        return create_result
    
    # Insert data
    insert_result = insert_dataframe(df, table_name)
    
    if insert_result["success"]:
        return {
            "success": True,
            "table_name": table_name,
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "upload_timestamp": insert_result["upload_timestamp"],
            "user_id": user_id
        }
    else:
        return insert_result


def get_table_preview(table_name: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get preview of table data.
    
    Args:
        table_name: Name of the table
        limit: Number of rows to return
    
    Returns:
        dict with preview data
    """
    table_name = sanitize_table_name(table_name)
    
    if not db_client.table_exists(table_name):
        return {
            "success": False,
            "error": f"Table '{table_name}' does not exist"
        }
    
    try:
        # Get table info
        columns_info = db_client.get_table_info(table_name)
        row_count = db_client.get_row_count(table_name)
        
        # Get sample rows
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        rows = db_client.query(query)
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": [col['name'] for col in columns_info],
            "row_count": row_count,
            "preview_rows": rows
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get preview: {str(e)}"
        }


def list_all_tables() -> List[Dict[str, Any]]:
    """
    List all tables with their metadata.
    
    Returns:
        List of table info dicts
    """
    tables = []
    
    for table_name in db_client.list_tables():
        try:
            row_count = db_client.get_row_count(table_name)
            columns_info = db_client.get_table_info(table_name)
            
            tables.append({
                "table_name": table_name,
                "row_count": row_count,
                "column_count": len(columns_info),
                "columns": [col['name'] for col in columns_info]
            })
        except Exception as e:
            continue
    
    return tables
