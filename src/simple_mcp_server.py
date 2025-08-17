#!/usr/bin/env python3
# Simple MCP server with a calculator function

from mcp.server.fastmcp import FastMCP

# Instantiate an MCP server instance with a name
mcp = FastMCP("CalculatorServer")

# Define a tool function using a decorator
@mcp.tool()
def add_numbers(x: float, y: float) -> float:
    """Add two numbers and return the result."""
    print(f"📝 Calculating: {x} + {y}")
    return x + y

# Additional calculator functions to show extensibility
@mcp.tool()
def subtract_numbers(x: float, y: float) -> float:
    """Subtract the second number from the first number."""
    print(f"📝 Calculating: {x} - {y}")
    return x - y

@mcp.tool()
def multiply_numbers(x: float, y: float) -> float:
    """Multiply two numbers together."""
    print(f"📝 Calculating: {x} * {y}")
    return x * y

@mcp.tool()
def divide_numbers(x: float, y: float) -> float:
    """Divide the first number by the second number."""
    if y == 0:
        error_msg = "Cannot divide by zero"
        print(f"❌ Error: {error_msg}")
        raise ValueError(error_msg)
    print(f"📝 Calculating: {x} / {y}")
    return x / y

if __name__ == "__main__":
    # This server will be launched automatically by the MCP stdio agent
    # You don't need to run this file directly - it will be spawned as a subprocess
    
    # Run the MCP server using standard input/output transport
    mcp.run(transport="stdio") 