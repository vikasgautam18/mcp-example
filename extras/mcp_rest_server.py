import requests
from mcp.server.core.mcp_server import MCPServer
from mcp.server.core.mcp_function import mcp_function

# Configuration for the mocked REST API
REST_API_BASE_URL = "http://127.0.0.1:5000"

class MockRestAPIMCPService:
    @mcp_function(
        name="get_all_products",
        description="Retrieves a list of all available products from the mocked REST API.",
        parameters={},
        returns={"type": "array", "items": {"type": "object"}},
    )
    def get_all_products(self):
        response = requests.get(f"{REST_API_BASE_URL}/products")
        response.raise_for_status()
        return response.json()

    @mcp_function(
        name="get_product_by_id",
        description="Retrieves a single product by its ID from the mocked REST API.",
        parameters={
            "product_id": {"type": "string", "description": "The ID of the product to retrieve."}
        },
        returns={"type": "object"},
    )
    def get_product_by_id(self, product_id: str):
        response = requests.get(f"{REST_API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return response.json()

    @mcp_function(
        name="get_all_orders",
        description="Retrieves a list of all orders from the mocked REST API.",
        parameters={},
        returns={"type": "array", "items": {"type": "object"}},
    )
    def get_all_orders(self):
        response = requests.get(f"{REST_API_BASE_URL}/orders")
        response.raise_for_status()
        return response.json()

    @mcp_function(
        name="create_order",
        description="Creates a new order for a product with a specified quantity.",
        parameters={
            "product_id": {"type": "string", "description": "The ID of the product to order."},
            "quantity": {"type": "integer", "description": "The quantity of the product to order."},
        },
        returns={"type": "object"},
    )
    def create_order(self, product_id: str, quantity: int):
        payload = {"product_id": product_id, "quantity": quantity}
        response = requests.post(f"{REST_API_BASE_URL}/orders", json=payload)
        response.raise_for_status()
        return response.json()

    @mcp_function(
        name="get_order_by_id",
        description="Retrieves a single order by its ID from the mocked REST API.",
        parameters={
            "order_id": {"type": "string", "description": "The ID of the order to retrieve."}
        },
        returns={"type": "object"},
    )
    def get_order_by_id(self, order_id: str):
        response = requests.get(f"{REST_API_BASE_URL}/orders/{order_id}")
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    server = MCPServer()
    server.register_service(MockRestAPIMCPService())
    server.start()
