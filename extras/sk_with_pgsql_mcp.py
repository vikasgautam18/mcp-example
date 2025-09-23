#!/usr/bin/env python3
# Semantic Kernel agent with MCP stdio plugin integration

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

async def main():
    # Load environment variables from .env file
    current_dir = pathlib.Path(__file__).parent
    env_path = current_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Find the correct path to the MCP server script
    mcp_server_path = current_dir / "pgsql_mcp_server.py"
    
    # Make sure the server script exists
    if not mcp_server_path.exists():
        print(f"Error: MCP server script not found at {mcp_server_path}")
        print(f"Make sure {mcp_server_path} is in the same directory as this script.")
        sys.exit(1)
    
    print("Setting up the Customer Details assistant with PGSQL MCP...")
    
    # Initialize the kernel
    kernel = Kernel()
    
    # Add an OpenAI service with function calling enabled
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("Error: AZURE_OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        sys.exit(1)
    
    service_id = "pgsql_mcp_demo_service"
    service = AzureChatCompletion(service_id=service_id, 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        )

    kernel.add_service(service)
    
    # Create the completion service request settings
    settings = OpenAIChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    
    # Configure and use the MCP plugin for our calculator using async context manager
    async with MCPStdioPlugin(
        name="PGSQLMCPServer", 
        command="python",
        args=[str(mcp_server_path)]  # Use absolute path to our MCP server script
    ) as mcp_plugin:
        # Register the MCP plugin with the kernel
        try:
            kernel.add_plugin(mcp_plugin, plugin_name="customer_details")
        except Exception as e:
            print(f"Error: Could not register the MCP plugin: {str(e)}")
            sys.exit(1)
        
        # Create a chat history with system instructions
        history = ChatHistory()
        history.add_system_message(
            "You are a highly skilled business analyst with extensive experience in writing SQL queries who has been tasked to query a set of tables from a database."
            "The database contains information about customers in the table customerdata. You must use customerdata table to answer questions about customers."
            "The table customerdata has the following columns: customer_id, card_blocked, payment_due, card_type and credit_card_no."
            "You have access to execute_query function which can execute SQL queries and return the result."
            "You must use the execute_query function to fetch data from the database."
            "Describe the customer details in words and do not return the raw data."
        )
        
        # Define a simple chat function
        chat_function = kernel.add_function(
            plugin_name="chat",
            function_name="respond", 
            prompt="{{$chat_history}}"
        )
        
        print("\n┌────────────────────────────────────────────┐")
        print("│ Customer Details Assistant ready with MCP    │")
        print("└────────────────────────────────────────────┘")
        print("Type 'exit' to end the conversation.")
        print("\nExample questions:")
        print("- Could you please fetch details of customer id 123456?")
        print("- Which customers have their card blocked?")
        print("- How many customers have a visa card?")
        
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
        print("\nExiting the Math Assistant. Goodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("The application has encountered a problem and needs to close.") 