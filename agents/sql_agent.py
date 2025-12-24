"""
SQL Agent - Converts natural language queries to SQL and executes them.
"""
from openai import OpenAI
from config.settings import OPENAI_API_KEY, LLM_MODEL
from database.sqlite_client import get_user_client
import json

# Initialize OpenAI client at module load
client = OpenAI(api_key=OPENAI_API_KEY)


def get_database_schema(user_id: str) -> str:
    """Get the current database schema for context from user-specific database."""
    db = get_user_client(user_id)
    tables = db.list_tables()
    
    if not tables:
        return "No tables in database."
    
    schema_info = []
    for table in tables:
        # Skip internal SQLite tables
        if table == 'sqlite_sequence':
            continue
            
        # Get table info
        columns = db.query(f"PRAGMA table_info({table})")
        
        col_details = []
        for col in columns:
            # Handle both dict and tuple results
            if isinstance(col, dict):
                col_name = col.get('name')
                col_type = col.get('type')
            else:
                col_name = col[1]
                col_type = col[2]
            
            # Skip internal columns
            if not col_name.startswith('_'):
                col_details.append(f"  - {col_name} ({col_type})")
        
        if col_details:  # Only add if there are non-internal columns
            schema_info.append(f"\nTable: {table}\nColumns:\n" + "\n".join(col_details))
    
    return "\n".join(schema_info) if schema_info else "No tables in database."


def generate_sql(user_query: str, schema: str) -> dict:
    """
    Generate SQL query from natural language using LLM.
    
    Returns:
        dict with 'sql', 'explanation', and 'needs_sql' keys
    """
    system_prompt = """You are an expert SQL assistant. Convert natural language questions into SQLite queries.

Given the database schema, generate a valid SQLite query.

Rules:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP)
2. Use proper SQLite syntax
3. Handle column names with spaces using quotes: "column name"
4. Be case-insensitive for column names
5. Use LIMIT to prevent huge results (default: 100)
6. If the question doesn't require SQL (greetings, general questions), set needs_sql to false

Return JSON with:
{
    "needs_sql": true/false,
    "sql": "SELECT ...",
    "explanation": "This query will...",
    "reasoning": "I interpreted your question as..."
}

Database Schema:
""" + schema

    response = client.chat.completions.create(
        model="gpt-5.1-codex",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate SQL query for safety.
    
    Returns:
        (is_valid, error_message)
    """
    sql_upper = sql.upper().strip()
    
    # Check for dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Dangerous operation '{keyword}' not allowed. Only SELECT queries permitted."
    
    # Must be SELECT
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT queries are allowed."
    
    return True, ""


def execute_sql(sql: str, user_id: str) -> dict:
    """
    Execute SQL query safely and return results from user-specific database.
    
    Args:
        sql: SQL query string
        user_id: User identifier for database isolation
    
    Returns:
        dict with 'success', 'data', 'row_count', and optionally 'error'
    """
    # Validate first
    is_valid, error = validate_sql(sql)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "data": [],
            "row_count": 0
        }
    
    try:
        db = get_user_client(user_id)
        results = db.query(sql)
        return {
            "success": True,
            "data": results,
            "row_count": len(results),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "row_count": 0
        }


def format_sql_results(results: list, limit: int = 10) -> str:
    """
    Format SQL results into a readable string.
    
    Args:
        results: List of Row objects or tuples from SQL query
        limit: Max rows to display
    """
    if not results:
        return "No results found."
    
    # Get first row to determine structure
    if not results[0]:
        return "Empty result set."
    
    # Convert Row objects to dicts if needed
    if hasattr(results[0], 'keys'):
        # It's a Row object
        headers = list(results[0].keys())
        data_rows = [[row[key] for key in headers] for row in results]
    else:
        # It's a tuple
        num_cols = len(results[0])
        headers = [f"Col{i+1}" for i in range(num_cols)]
        data_rows = results
    
    # Format as markdown table
    output = []
    
    # Show limited rows
    display_rows = data_rows[:limit]
    
    # Create header
    output.append("| " + " | ".join(headers) + " |")
    output.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # Add data rows
    for row in display_rows:
        formatted_row = [str(val) if val is not None else "NULL" for val in row]
        output.append("| " + " | ".join(formatted_row) + " |")
    
    # Add summary
    if len(data_rows) > limit:
        output.append(f"\n... and {len(data_rows) - limit} more rows")
    
    output.append(f"\nTotal rows: {len(data_rows)}")
    
    return "\n".join(output)


def text_to_sql(user_query: str, user_id: str) -> dict:
    """
    Main function: Convert natural language to SQL and execute.
    
    Args:
        user_query: Natural language query
        user_id: User identifier for database isolation
    
    Returns:
        dict with query results and metadata
    """
    # Get schema from user-specific database
    schema = get_database_schema(user_id)
    
    if schema == "No tables in database.":
        return {
            "success": False,
            "needs_sql": False,
            "message": "No data tables found. Please upload CSV files first.",
            "data": [],
            "sql": None
        }
    
    # Generate SQL
    sql_result = generate_sql(user_query, schema)
    
    # Check if SQL is needed
    if not sql_result.get("needs_sql", True):
        return {
            "success": False,
            "needs_sql": False,
            "message": sql_result.get("explanation", "This question doesn't require database access."),
            "data": [],
            "sql": None
        }
    
    sql_query = sql_result.get("sql", "")
    explanation = sql_result.get("explanation", "")
    reasoning = sql_result.get("reasoning", "")
    
    # Execute SQL on user-specific database
    exec_result = execute_sql(sql_query, user_id)
    
    if not exec_result["success"]:
        return {
            "success": False,
            "needs_sql": True,
            "sql": sql_query,
            "error": exec_result["error"],
            "explanation": explanation,
            "data": [],
            "message": f"SQL execution failed: {exec_result['error']}"
        }
    
    # Format results
    formatted_data = format_sql_results(exec_result["data"])
    
    return {
        "success": True,
        "needs_sql": True,
        "sql": sql_query,
        "explanation": explanation,
        "reasoning": reasoning,
        "data": exec_result["data"],
        "formatted_data": formatted_data,
        "row_count": exec_result["row_count"],
        "message": f"Query executed successfully. Found {exec_result['row_count']} rows."
    }


if __name__ == "__main__":
    # Test the SQL agent
    print("🗄️  Testing SQL Agent\n")
    
    test_queries = [
        "Show me all employees",
        "What's the average salary?",
        "Find employees with salary > 50000",
        "How many employees are there?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = text_to_sql(query)
        
        if result["success"]:
            print(f"✅ SQL: {result['sql']}")
            print(f"📊 Results:\n{result['formatted_data']}")
        else:
            print(f"❌ {result['message']}")
