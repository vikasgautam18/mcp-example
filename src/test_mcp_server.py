#!/usr/bin/env python3
# Semantic Kernel agent with MCP stdio plugin integration to test mcp_server.py

import asyncio
import os
import sys
import pathlib
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.streaming_chat_message_content import StreamingChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import anyio

async def main():
    # Load environment variables from .env file
    current_dir = pathlib.Path(__file__).parent
    env_path = current_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Find the correct path to the MCP server script
    mcp_server_path = current_dir / "mcp_server.py"
    
    # Make sure the server script exists
    if not mcp_server_path.exists():
        print(f"Error: MCP server script not found at {mcp_server_path}")
        sys.exit(1)
    
    print("Setting up the API Assistant with MCP tools...")
    
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
    
    # Create the completion service request settings
    settings = OpenAIChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    
    # Configure and use the MCP plugin for our API server using async context manager
    async with MCPStdioPlugin(
        name="APIMCPServer", 
        command="python",
        args=[str(mcp_server_path)]
    ) as mcp_plugin:
        # Register the MCP plugin with the kernel
        try:
            kernel.add_plugin(mcp_plugin, plugin_name="api")
        except Exception as e:
            print(f"Error: Could not register the MCP plugin: {str(e)}")
            sys.exit(1)
        
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
        print("│ API Assistant ready with MCP Tools         │")
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
        anyio.run(main)
    except KeyboardInterrupt:
        print("\nExiting the API Assistant. Goodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
