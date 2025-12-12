# # app/components/tools.py

# import os
# import sqlite3
# import json
# from typing import List, Dict, Any

# from langchain.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults


# # ---------- Tavily client (low-level) ---------- #

# tavily_client = TavilySearchResults(
#     max_results=5,
#     include_answer=True,
# )


# @tool
# def tavily_custom_search(query: str) -> str:
#     """
#     Use Tavily web search to answer user questions with a concise,
#     helpful response.

#     This wrapper:
#     - Uses your Tavily API key from the environment.
#     - Returns Tavily's summarized answer as a string.
#     - Is the ONLY Tavily-facing tool exposed to agents.
#     """
#     print(f"[TOOL] tavily_custom_search called with query={query!r}")
#     return tavily_client.run(query)


# # ---------- SQLite DB tool (READ-ONLY) ---------- #

# # Path controlled by env var SQLITE_DB_PATH, defaulting to data/app.db
# SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/app.db")


# @tool
# def sqlite_select_tool(query: str) -> str:
#     """
#     Run a READ-ONLY SELECT query on the SQLite database.

#     RULES:
#     - Query MUST start with 'SELECT' (case-insensitive).
#     - No multiple statements (no extra semicolons).
#     - Always prefer queries with LIMIT.

#     Input:
#         query: A full SQL SELECT statement, e.g.
#             "SELECT id, name FROM users WHERE age > 30 LIMIT 10"

#     Output (as JSON string):
#         {
#           "rows": [ { "col": value, ... }, ... ],
#           "row_count": <int>
#         }
#         or an "error" field if something goes wrong.
#     """
#     print(f"[TOOL] sqlite_select_tool called with query={query!r}")
#     q = query.strip().lower()
#     if not q.startswith("select"):
#         return json.dumps(
#             {
#                 "error": "Only SELECT queries are allowed. Your query must start with 'SELECT'.",
#                 "original_query": query,
#             }
#         )

#     if ";" in query:
#         return json.dumps(
#             {
#                 "error": "Multiple statements are not allowed. Remove extra semicolons.",
#                 "original_query": query,
#             }
#         )

#     if not os.path.exists(SQLITE_DB_PATH):
#         return json.dumps(
#             {
#                 "error": f"SQLite DB file not found at {SQLITE_DB_PATH}",
#                 "original_query": query,
#             }
#         )

#     try:
#         conn = sqlite3.connect(SQLITE_DB_PATH)
#         conn.row_factory = sqlite3.Row
#         cur = conn.cursor()
#         cur.execute(query)
#         rows = cur.fetchall()
#         conn.close()

#         result_rows: List[Dict[str, Any]] = [dict(row) for row in rows]

#         return json.dumps(
#             {
#                 "rows": result_rows,
#                 "row_count": len(result_rows),
#             },
#             default=str,
#         )
#     except Exception as e:
#         return json.dumps(
#             {
#                 "error": f"SQLite query failed: {e}",
#                 "original_query": query,
#             }
#         )


# # ---------- Math tool ---------- #

# @tool
# def math_tool(expression: str) -> str:
#     """
#     Evaluate a simple math expression (Python syntax).

#     Examples:
#     - "15 * (4 + 3)"
#     - "100 / 3"
#     """
#     try:
#         print(f"[TOOL] math_tool called with expression={expression!r}")
#         result = eval(expression, {"__builtins__": {}})
#         return f"Result: {result}"
#     except Exception as e:
#         return f"Error in expression: {e}"




# # app/components/tools.py

# import os
# import sqlite3
# import json
# from typing import List, Dict, Any

# from langchain_core.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults


# # ---------- Tavily (web search) ---------- #

# tavily_client = TavilySearchResults(
#     max_results=5,
#     include_answer=True,
# )


# @tool
# def tavily_custom_search(query: str) -> str:
#     """
#     Use Tavily web search to answer user questions with a concise,
#     helpful response.

#     This wrapper:
#     - Uses your Tavily API key from the environment.
#     - Returns Tavily's summarized answer as a string.
#     - Logs calls for debugging.
#     """
#     print(f"[TOOL] tavily_custom_search called with query={query!r}")
#     return tavily_client.run(query)


# # ---------- SQLite DB tool (READ-ONLY) ---------- #

# # Path controlled by env var SQLITE_DB_PATH, defaulting to data/app.db
# SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/app.db")


# @tool
# def sqlite_select_tool(query: str) -> str:
#     """
#     Run a READ-ONLY SELECT query on the SQLite database.

#     RULES:
#     - Query MUST start with 'SELECT' (case-insensitive).
#     - No multiple statements (no extra semicolons).
#     - Always prefer queries with LIMIT.

#     Input:
#         query: A full SQL SELECT statement, e.g.
#             "SELECT id, name FROM users WHERE age > 30 LIMIT 10"

#     Output (as JSON string):
#         {
#           "rows": [ { "col": value, ... }, ... ],
#           "row_count": <int>
#         }
#         or an "error" field if something goes wrong.
#     """
#     print(f"[TOOL] sqlite_select_tool called with query={query!r}")

#     q = query.strip().lower()
#     if not q.startswith("select"):
#         return json.dumps(
#             {
#                 "error": "Only SELECT queries are allowed. Your query must start with 'SELECT'.",
#                 "original_query": query,
#             }
#         )

#     if ";" in query:
#         return json.dumps(
#             {
#                 "error": "Multiple statements are not allowed. Remove extra semicolons.",
#                 "original_query": query,
#             }
#         )

#     if not os.path.exists(SQLITE_DB_PATH):
#         return json.dumps(
#             {
#                 "error": f"SQLite DB file not found at {SQLITE_DB_PATH}",
#                 "original_query": query,
#             }
#         )

#     try:
#         conn = sqlite3.connect(SQLITE_DB_PATH)
#         conn.row_factory = sqlite3.Row
#         cur = conn.cursor()
#         cur.execute(query)
#         rows = cur.fetchall()
#         conn.close()

#         result_rows: List[Dict[str, Any]] = [dict(row) for row in rows]

#         return json.dumps(
#             {
#                 "rows": result_rows,
#                 "row_count": len(result_rows),
#             },
#             default=str,
#         )
#     except Exception as e:
#         return json.dumps(
#             {
#                 "error": f"SQLite query failed: {e}",
#                 "original_query": query,
#             }
#         )


# # ---------- Math tool ---------- #

# @tool
# def math_tool(expression: str) -> str:
#     """
#     Evaluate a simple math expression (Python syntax).

#     Examples:
#     - "15 * (4 + 3)"
#     - "100 / 3"
#     """
#     print(f"[TOOL] math_tool called with expression={expression!r}")
#     try:
#         result = eval(expression, {"__builtins__": {}})
#         return f"Result: {result}"
#     except Exception as e:
#         return f"Error in expression: {e}"




# app/components/tools.py

import os
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


# ============================================================
# DB PATH RESOLUTION
# ============================================================

CURR_FILE = Path(__file__).resolve()
APP_DIR = CURR_FILE.parents[1]

# Default DB path: app/db/app.db:
DEFAULT_DB_PATH = APP_DIR / "db" / "app.db"

# Allow override via env var, else use app/db/app.db
SQLITE_DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(DEFAULT_DB_PATH)))


# ============================================================
# TAVILY WEB SEARCH TOOL
# ============================================================

# Tavily client; expects TAVILY_API_KEY in your environment
tavily_client = TavilySearchResults(
    max_results=5,
    include_answer=True,
)


@tool
def tavily_custom_search(query: str) -> str:
    """
    Use Tavily web search to answer user questions with a concise,
    helpful response.

    Input:
        query: The search query string.

    Output:
        A string containing Tavily's summarized answer or search result.
    """
    print(f"[TOOL] tavily_custom_search called with query={query!r}")
    try:
        return tavily_client.run(query)
    except Exception as e:
        return f"Error while performing Tavily search: {e}"


# ============================================================
# SQLITE DB SELECT TOOL (Customer orders only)
# ============================================================


@tool
def sqlite_select_tool(query: str) -> str:
    """
    Run a READ-ONLY SELECT query on the SQLite database.

    RULES:
    - Only SELECT queries are allowed (case-insensitive check).
    - No multiple statements (no extra semicolons).
    - Prefer queries with LIMIT for safety.

    Input:
        query: A full SQL SELECT statement, e.g.
            "SELECT id, name FROM users WHERE city = 'Kyoto' LIMIT 10"

    Output:
        JSON string with either:
        {
          "rows": [ { "col": value, ... }, ... ],
          "row_count": <int>
        }
        or
        {
          "error": "<error message>",
          "original_query": "<the query>"
        }
    """
    print(f"[TOOL] sqlite_select_tool called with query={query!r}")

    stripped = query.strip()
    lowered = stripped.lower()

    # Basic safety checks
    if not lowered.startswith("select"):
        return json.dumps(
            {
                "error": "Only SELECT queries are allowed. Your query must start with 'SELECT'.",
                "original_query": query,
            }
        )

    if ";" in stripped:
        # Disallow multiple statements
        return json.dumps(
            {
                "error": "Multiple statements / semicolons are not allowed. Use a single SELECT statement.",
                "original_query": query,
            }
        )

    if not SQLITE_DB_PATH.exists():
        return json.dumps(
            {
                "error": f"SQLite DB file not found at {SQLITE_DB_PATH}",
                "original_query": query,
            }
        )

    try:
        conn = sqlite3.connect(str(SQLITE_DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        result_rows: List[Dict[str, Any]] = [dict(row) for row in rows]

        return json.dumps(
            {
                "rows": result_rows,
                "row_count": len(result_rows),
            },
            default=str,  # handle datetime, etc.
        )
    except Exception as e:
        return json.dumps(
            {
                "error": f"SQLite query failed: {e}",
                "original_query": query,
            }
        )


# ============================================================
# MATH TOOL
# ============================================================


@tool
def math_tool(expression: str) -> str:
    """
    Evaluate a simple math expression using Python syntax.

    Examples:
        "15 * (4 + 3)"
        "100 / 3"
        "2 ** 10"

    Input:
        expression: A math expression as a string.

    Output:
        A string: either "Result: <value>" or "Error in expression: <msg>".
    """
    print(f"[TOOL] math_tool called with expression={expression!r}")
    try:
        # Evaluate expression in a restricted environment
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error in expression: {e}"




@tool
def get_customer_clinical_summary(customer_id: str) -> str:
    """
    Get the most recent, detailed clinical summary text for a given customer_id.

    Returns ONE long narrative (doctor notes / history / guidance) that
    the MEDICAL agent will use to answer questions.
    """
    print(f"[TOOL] get_customer_clinical_summary called with customer_id={customer_id}")

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT summary_text
        FROM clinical_summaries
        WHERE customer_id = ?
        ORDER BY datetime(created_at) DESC
        LIMIT 1
        """,
        (customer_id,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return f"No clinical summary found for customer_id={customer_id!r}."

    (summary_text,) = row
    return summary_text