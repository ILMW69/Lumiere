"""
SQL Reasoning Agent - Interprets SQL results and generates natural language responses.
"""
from langchain_openai import ChatOpenAI
from config.settings import LLM_MODEL

# Initialize ChatOpenAI client at module load
llm = ChatOpenAI(
    model_name=LLM_MODEL,
)

SQL_REASONING_PROMPT = """You are a data analysis assistant. Your job is to interpret SQL query results and provide clear, natural language answers.

User Question:
{question}

SQL Query Executed:
{sql_query}

Query Results:
{results}

Row Count: {row_count}

Instructions:
1. Provide a clear, natural language answer to the user's question
2. Highlight key insights from the data
3. If results are empty, explain that no matching data was found
4. If there are many rows, summarize the key findings
5. Be conversational and helpful
6. Format numbers nicely (e.g., "$50,000" instead of "50000")

Generate a helpful response:"""


def sql_reasoning_agent(state):
    """
    Generate natural language response from SQL results.
    """
    question = state.get("question", "")
    sql_results = state.get("sql_results", {})
    
    if not sql_results or not sql_results.get("success"):
        # SQL execution failed
        error_msg = sql_results.get("error", "Unknown error")
        state["answer"] = f"I encountered an error while querying the database: {error_msg}"
        state["reasoning_mode"] = "sql"
        return state
    
    sql_query = sql_results.get("sql", "")
    data = sql_results.get("data", [])
    row_count = sql_results.get("row_count", 0)
    formatted_data = sql_results.get("formatted_data", "No data")
    
    # Generate natural language response
    
    response = llm.invoke(
        SQL_REASONING_PROMPT.format(
            question=question,
            sql_query=sql_query,
            results=formatted_data,
            row_count=row_count
        )
    )
    
    answer = response.content.strip()
    
    # Store SQL query separately for transparency (optional: can be shown in UI)
    # If you want to show the SQL query, uncomment the line below:
    # answer += f"\n\n---\n**SQL Query:**\n```sql\n{sql_query}\n```"
    
    state["answer"] = answer
    state["reasoning_mode"] = "sql"
    
    return state
