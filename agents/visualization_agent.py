"""
Visualization Agent - Automatically generates charts from SQL query results.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
import pandas as pd

def visualization_agent(state: dict) -> dict:
    """
    Analyzes SQL results and generates appropriate visualizations.
    
    Args:
        state: Graph state containing sql_results
        
    Returns:
        Updated state with visualization_config
    """
    sql_results = state.get("sql_results", {})
    
    if not sql_results or not sql_results.get("success"):
        state["visualization_config"] = None
        return state
    
    data = sql_results.get("data", [])
    columns = sql_results.get("columns", [])
    
    # If columns not provided, extract from first row (Row objects are dicts)
    if not columns and data and len(data) > 0:
        if hasattr(data[0], 'keys'):
            columns = list(data[0].keys())
        elif isinstance(data[0], dict):
            columns = list(data[0].keys())
    
    if not data or not columns or len(data) == 0:
        state["visualization_config"] = None
        return state
    
    # Convert Row objects to list of lists for DataFrame
    if hasattr(data[0], 'keys'):
        # It's a Row object
        data_list = [[row[col] for col in columns] for row in data]
    elif isinstance(data[0], dict):
        # It's a dict
        data_list = [[row[col] for col in columns] for row in data]
    else:
        # Already a list of lists
        data_list = data
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(data_list, columns=columns)
    
    # Analyze data structure
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Prepare data summary for LLM
    data_summary = {
        "columns": columns,
        "row_count": len(df),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "sample_data": data_list[:5],  # First 5 rows as list of lists
        "column_stats": {}
    }
    
    # Add statistics for numeric columns
    for col in numeric_cols:
        data_summary["column_stats"][col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
            "count": int(df[col].count())
        }
    
    # Add value counts for categorical columns (if reasonable size)
    for col in categorical_cols:
        unique_count = df[col].nunique()
        if unique_count <= 20:  # Only for columns with reasonable unique values
            data_summary["column_stats"][col] = {
                "unique_count": unique_count,
                "top_values": df[col].value_counts().head(10).to_dict()
            }
    
    # Use LLM to determine best visualization
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    system_prompt = """You are a data visualization expert. Analyze the SQL query results and determine the best chart type.

Available chart types:
- bar: For comparing categories (e.g., sales by region, count by category)
- line: For trends over time or continuous data
- pie: For showing proportions of a whole (max 10 categories)
- scatter: For showing relationships between two numeric variables
- histogram: For showing distribution of a single numeric variable
- table: For detailed data inspection (fallback)

Return a JSON object with this structure:
{
    "chart_type": "bar|line|pie|scatter|histogram|table",
    "x_column": "column name for x-axis",
    "y_column": "column name for y-axis (or value)",
    "title": "descriptive chart title",
    "reasoning": "why this chart type was chosen"
}

Guidelines:
- If only 1 column: use histogram for numeric, bar for categorical
- If 2 columns (1 categorical + 1 numeric): use bar chart
- If 2 numeric columns: use scatter plot
- If time-based data: use line chart
- If showing parts of whole (percentages, counts with few categories): use pie chart
- Pie charts should have max 10 categories
- Choose the chart that best communicates the data story
"""
    
    user_prompt = f"""SQL Query Results Summary:

Columns: {columns}
Row Count: {len(data)}
Numeric Columns: {numeric_cols}
Categorical Columns: {categorical_cols}

Sample Data (first 5 rows):
{json.dumps(data[:5], indent=2)}

Column Statistics:
{json.dumps(data_summary["column_stats"], indent=2)}

Determine the best visualization for this data."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        
        # Extract JSON from response
        response_text = response.content.strip()
        
        # Handle code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        viz_config = json.loads(response_text)
        
        # Add data to config (use converted list format)
        viz_config["data"] = data_list
        viz_config["columns"] = columns
        
        state["visualization_config"] = viz_config
        return state
        
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        # Fallback to simple bar chart if we have the right data structure
        if len(numeric_cols) > 0 and len(categorical_cols) > 0:
            state["visualization_config"] = {
                "chart_type": "bar",
                "x_column": categorical_cols[0],
                "y_column": numeric_cols[0],
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "data": data_list,
                "columns": columns,
                "reasoning": "Fallback: bar chart for categorical vs numeric data"
            }
            return state
        else:
            state["visualization_config"] = {
                "chart_type": "table",
                "title": "Query Results",
                "data": data_list,
                "columns": columns,
                "reasoning": "Fallback: table view for complex data"
            }
            return state


def should_visualize(state: dict) -> bool:
    """
    Determines if visualization should be generated.
    Only visualize in data_analyst mode with successful SQL results.
    """
    mode = state.get("lumiere_mode", "all_in")
    sql_results = state.get("sql_results", {})
    
    # Only visualize in data analyst mode
    if mode != "data_analyst":
        return False
    
    # Must have successful SQL results
    if not sql_results or not sql_results.get("success"):
        return False
    
    # Must have data
    data = sql_results.get("data", [])
    if not data or len(data) == 0:
        return False
    
    return True
