#!/usr/bin/env python3
# Simple MCP server with a calculator function

from mcp.server.fastmcp import FastMCP
import psycopg2, os, json, sys
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Connect to the PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise e

# Instantiate an MCP server instance with a name
mcp = FastMCP("PGSQLMCPServer")

# Connect to the database
db_conn = connect_db()

# Ensure the database connection is established before starting the server
if not db_conn:
    print("❌ Could not connect to the database. Exiting.")
    sys.exit(1)
else:
    print("✅ Database connection established.")


# Ensure the database connection is closed when the server stops

def close_db_connection():
    if db_conn:
        db_conn.close()
        print("✅ Database connection closed.")
    else:
        print("⚠️ No database connection to close.")

# Define a tool function using a decorator

@mcp.tool()
def execute_query(query, params=None):
    """Execute a SQL query and return the result."""
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if cursor.description:  # If the query returns rows
                return cursor.fetchall()
            
            db_conn.commit()  # Commit if it's an insert/update/delete
    except Exception as e:
        print(f"❌ Query execution error: {e}")
        raise e

# @mcp.tool()
# def get_customer_details(customer_id: int):
#     """Get customer details by ID."""
#     query = "SELECT * FROM customerdata WHERE customer_id = %s"
#     result = execute_query(query, (customer_id,))

#     result_record = result[0] if result else None
#     if result_record:
#         # Convert Decimal values to strings
#         for key, value in result_record.items():
#             if isinstance(value, Decimal):
#                 result_record[key] = str(value)
#         return json.dumps({"result_record": result_record})
#     else:
#         return json.dumps({"error": "An error occured while fetching the data."})


if __name__ == "__main__":
    # This server will be launched automatically by the MCP stdio agent
    # You don't need to run this file directly - it will be spawned as a subprocess
    
    # Run the MCP server using standard input/output transport
    mcp.run(transport="stdio") 