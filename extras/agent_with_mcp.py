import semantic_kernel as sk
import semantic_kernel.connectors.ai.open_ai as sk_oai
import os
import sys
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.functions import KernelArguments
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
import asyncio

# Configuration for the mocked REST API
REST_API_BASE_URL = "http://127.0.0.1:5000"

from dotenv import load_dotenv
load_dotenv()

async def main(prompt: str):
    kernel = sk.Kernel()

    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

    # print azure openai config
    print(f"Azure OpenAI Endpoint: {azure_openai_endpoint}")
    print(f"Azure OpenAI Deployment Name: {azure_openai_deployment_name}")  
    print(f"Azure OpenAI API Key: {azure_openai_api_key[:5]}...")


    if not all([azure_openai_endpoint, azure_openai_api_key, azure_openai_deployment_name]):
        print("Error: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and MODEL_DEPLOYMENT_NAME environment variables must be set.")
        sys.exit(1)

    kernel.add_service(
        sk_oai.AzureChatCompletion(
            service_id="chat-gpt",
            deployment_name=azure_openai_deployment_name,
            endpoint=azure_openai_endpoint,
            api_key=azure_openai_api_key,
        ),
    )

    # Add the MCP stdio plugin to the kernel
    # Find the correct path to the MCP server script
    mcp_server_path = "src/mcp_server.py"

    mcp_plugin = MCPStdioPlugin(
            name="APIMCPServer",
            command="python",
            args=[mcp_server_path]  # Use absolute path to our MCP server script
        )
        
        # It's important to start the plugin process
    await mcp_plugin.__aenter__()

    kernel.add_plugin(mcp_plugin, "APIMCPServer")

    # Create a semantic function to answer questions using the plugin
    chat_function = kernel.add_function(
        plugin_name="chat",
        function_name="respond",
        prompt="""
        You are a helpful assistant that can answer questions about products and orders.
        Use the available tools to get information. If you need to create an order, ask for confirmation.
        
        User: {{$input}}
        Assistant: """
    )

    history = ChatHistory()
    # Add the user message to history
    history.add_user_message(prompt)

    # Create the completion service request settings
    settings = OpenAIChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

    # Prepare arguments with history and settings
    arguments = KernelArguments(
        settings=settings,
        chat_history=history,
        input=prompt,
    )


    result = await kernel.invoke(chat_function, arguments=arguments)
    # read only the text part of the result
    
    print(f"Response: {result}")

    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_no_mcp.py <prompt>")
        sys.exit(1)
    prompt = sys.argv[1]
    asyncio.run(main(prompt))