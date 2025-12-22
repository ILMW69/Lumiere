"""
SQLite client for managing database operations.
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class SQLiteClient:
    """SQLite database client for Lumiere."""
    
    def __init__(self, db_path: str = "lumiere.db"):
        """
        Initialize SQLite client.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Store in project root
        project_root = Path(__file__).parent.parent
        self.db_path = project_root / db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        if not self.connection:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        return self.connection
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            Cursor object
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        return cursor
    
    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dicts.
        
        Args:
            sql: SELECT query
            params: Query parameters (optional)
        
        Returns:
            List of row dictionaries
        """
        cursor = self.execute(sql, params)
        columns = [description[0] for description in cursor.description] if cursor.description else []
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def list_tables(self) -> List[str]:
        """
        List all tables in the database.
        
        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.query(query)
        return [row['name'] for row in results]
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists.
        
        Args:
            table_name: Name of the table
        
        Returns:
            True if table exists, False otherwise
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        results = self.query(query, (table_name,))
        return len(results) > 0
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of column info dicts
        """
        query = f"PRAGMA table_info({table_name})"
        return self.query(query)
    
    def get_row_count(self, table_name: str) -> int:
        """
        Get number of rows in a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Row count
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.query(query)
        return result[0]['count'] if result else 0
    
    def drop_table(self, table_name: str) -> bool:
        """
        Drop a table.
        
        Args:
            table_name: Name of the table to drop
        
        Returns:
            True if successful
        """
        try:
            # Sanitize table name to prevent SQL injection
            # Only allow alphanumeric and underscore
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
                print(f"Invalid table name: {table_name}")
                return False
            
            # Execute DROP TABLE
            query = f"DROP TABLE IF EXISTS `{table_name}`"
            print(f"Executing: {query}")
            self.execute(query)
            print(f"Successfully dropped table: {table_name}")
            return True
        except Exception as e:
            print(f"Error dropping table {table_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client instance
client = SQLiteClient()
