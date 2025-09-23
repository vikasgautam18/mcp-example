#!/usr/bin/env python3
# Semantic Kernel agent to test API functions directly

import asyncio
import os
import sys
import pathlib
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.streaming_chat_message_content import StreamingChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelArguments, kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import requests
import json

# Configuration for the mocked REST API
REST_API_BASE_URL = "http://127.0.0.1:5000"

class ApiPlugin:
    @kernel_function(
        name="get_all_products",
        description="Retrieves a list of all available products from the mocked REST API.",
    )
    def get_all_products(self) -> str:
        response = requests.get(f"{REST_API_BASE_URL}/products")
        response.raise_for_status()
        return json.dumps(response.json())

    @kernel_function(
        name="get_product_by_id",
        description="Retrieves a single product by its ID from the mocked REST API."
    )
    def get_product_by_id(self, product_id: str) -> str:
        response = requests.get(f"{REST_API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return json.dumps(response.json())

    @kernel_function(
        name="get_all_orders",
        description="Retrieves a list of all orders from the mocked REST API.",
    )
    def get_all_orders(self) -> str:
        response = requests.get(f"{REST_API_BASE_URL}/orders")
        response.raise_for_status()
        return json.dumps(response.json())

    @kernel_function(
        name="create_order",
        description="Creates a new order for a product with a specified quantity."
    )
    def create_order(self, product_id: str, quantity: int) -> str:
        payload = {"product_id": product_id, "quantity": quantity}
        response = requests.post(f"{REST_API_BASE_URL}/orders", json=payload)
        response.raise_for_status()
        return json.dumps(response.json())

    @kernel_function(
        name="get_order_by_id",
        description="Retrieves a single order by its ID from the mocked REST API."
    )
    def get_order_by_id(self, order_id: str) -> str:
        response = requests.get(f"{REST_API_BASE_URL}/orders/{order_id}")
        response.raise_for_status()
        return json.dumps(response.json())

async def main():
    # Load environment variables from .env file
    current_dir = pathlib.Path(__file__).parent
    env_path = current_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    print("Setting up the API Assistant...")
    
    # Initialize the kernel
    kernel = Kernel()
    
    # Add an OpenAI service with function calling enabled
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("Error: AZURE_OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)
    
    service_id = "api_test_service"
    service = AzureChatCompletion(service_id=service_id, 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        )

    kernel.add_service(service)
    
    # Add the API plugin to the kernel
    kernel.add_plugin(ApiPlugin(), plugin_name="api")
    
    # Create the completion service request settings
    settings = OpenAIChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    
    # Create a chat history with system instructions
    history = ChatHistory()
    history.add_system_message(
        "You are an API assistant. Use the available tools to interact with the API."
        "You have access to tools for products and orders."
    )
    
    # Define a simple chat function
    chat_function = kernel.add_function(
        plugin_name="chat",
        function_name="respond", 
        prompt="{{$chat_history}}"
    )
    
    print("\n┌────────────────────────────────────────────┐")
    print("│ API Assistant ready                        │")
    print("└────────────────────────────────────────────┘")
    print("Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("\nUser:> ")
        if user_input.lower() == "exit":
            break
            
        # Add the user message to history
        history.add_user_message(user_input)
        
        # Prepare arguments with history and settings
        arguments = KernelArguments(
            chat_history=history,
            settings=settings
        )
        
        try:
            # Stream the response
            print("Assistant:> ", end="", flush=True)
            
            response_chunks = []
            async for message in kernel.invoke_stream(
                chat_function,
                arguments=arguments
            ):
                chunk = message[0]
                if isinstance(chunk, StreamingChatMessageContent) and chunk.role == AuthorRole.ASSISTANT:
                    print(str(chunk), end="", flush=True)
                    response_chunks.append(chunk)
            
            print()  # New line after response
            
            # Add the full response to history
            full_response = "".join(str(chunk) for chunk in response_chunks)
            history.add_assistant_message(full_response)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try another question.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting the API Assistant. Goodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
