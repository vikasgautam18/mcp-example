import asyncio
import subprocess
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure Azure OpenAI credentials are set
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME]):
    print("Error: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT_NAME environment variables must be set.")
    print("Please set them in your .env file or environment variables.")
    exit(1)

# Paths to the scripts
REST_API_SCRIPT = "src/mock_rest_api.py"
MCP_SERVER_SCRIPT = "src/mcp_rest_server.py"
AGENT_NO_MCP_SCRIPT = "src/agent_no_mcp.py"
AGENT_WITH_MCP_SCRIPT = "src/agent_with_mcp.py"

async def run_agent_interaction(agent_script: str, prompt: str):
    print(f"\n--- Running {agent_script} with prompt: '{prompt}' ---")
    env = os.environ.copy()
    env["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    env["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
    env["AZURE_OPENAI_DEPLOYMENT_NAME"] = AZURE_OPENAI_DEPLOYMENT_NAME

    process = await asyncio.create_subprocess_exec(
        "python",
        agent_script,
        prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )
    stdout, stderr = await process.communicate()

    if stdout:
        print(f"STDOUT:\n{stdout.decode().strip()}")
    if stderr:
        print(f"STDERR:\n{stderr.decode().strip()}")
    if process.returncode != 0:
        print(f"Error: {agent_script} exited with code {process.returncode}")

async def main():
    # Start the mocked REST API server
    print(f"Starting Mock REST API server ({REST_API_SCRIPT})...")
    rest_api_process = subprocess.Popen(["python", REST_API_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3) # Give the server some time to start
    print("Mock REST API server started.")

    # Start the MCP server
    print(f"Starting MCP server ({MCP_SERVER_SCRIPT})...")
    mcp_server_process = subprocess.Popen(["python", MCP_SERVER_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3) # Give the server some time to start
    print("MCP server started.")

    try:
        prompts = [
            "List all products.",
            "What is the price of product with ID 1?",
            "Create an order for product ID 2 with quantity 5.",
            "List all orders."
        ]

        print("\n==================================================")
        print("DEMO: Agent without MCP")
        print("==================================================")
        for prompt in prompts:
            await run_agent_interaction(AGENT_NO_MCP_SCRIPT, prompt)

        print("\n==================================================")
        print("DEMO: Agent with MCP")
        print("==================================================")
        for prompt in prompts:
            await run_agent_interaction(AGENT_WITH_MCP_SCRIPT, prompt)

    finally:
        # Shut down the servers
        print("\nShutting down servers...")
        rest_api_process.terminate()
        mcp_server_process.terminate()
        rest_api_process.wait()
        mcp_server_process.wait()
        print("Servers shut down.")

if __name__ == "__main__":
    asyncio.run(main())
