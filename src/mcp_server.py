#!/usr/bin/env python3
# Simple MCP server with a calculator function

from mcp.server.fastmcp import FastMCP
import requests

# Instantiate an MCP server instance with a name
mcp = FastMCP("APIMCPServer")

# Configuration for the mocked REST API
REST_API_BASE_URL = "http://127.0.0.1:5000"

# Define a tool function using a decorator
@mcp.tool()
def get_all_products():
        response = requests.get(f"{REST_API_BASE_URL}/products")
        response.raise_for_status()
        return response.json()

# Additional calculator functions to show extensibility
@mcp.tool()
def get_product_by_id(product_id: str):
        response = requests.get(f"{REST_API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return response.json()

@mcp.tool()
def get_all_orders():
        response = requests.get(f"{REST_API_BASE_URL}/orders")
        response.raise_for_status()
        return response.json()

@mcp.tool()
def create_order(product_id: str, quantity: int):
        payload = {"product_id": product_id, "quantity": quantity}
        response = requests.post(f"{REST_API_BASE_URL}/orders", json=payload)
        response.raise_for_status()
        return response.json()

@mcp.tool()
def get_order_by_id(order_id: str):
        response = requests.get(f"{REST_API_BASE_URL}/orders/{order_id}")
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    # This server will be launched automatically by the MCP stdio agent
    # You don't need to run this file directly - it will be spawned as a subprocess
    print("Starting MCP server...")
    # Run the MCP server using standard input/output transport
    mcp.run(transport="stdio")