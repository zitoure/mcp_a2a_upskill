from dotenv import load_dotenv
from openai import AzureOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import List
import asyncio
import nest_asyncio
import os
import json

nest_asyncio.apply()

load_dotenv()

class MCP_ChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession = None
        self.azure_openai = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.available_tools: List[dict] = []

    async def process_query(self, query):
        messages = [{'role':'user', 'content':query}]
        response = self.azure_openai.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"), 
            tools=self.available_tools,
            messages=messages,
            max_tokens=2024
        )
        
        process_query = True
        while process_query:
            assistant_content = []
            message = response.choices[0].message
            
            if message.content:
                print(message.content)
                assistant_content.append({"type": "text", "text": message.content})
                if not message.tool_calls:
                    process_query = False
                    
            if message.tool_calls:
                # Add assistant message with tool calls
                messages.append({
                    'role': 'assistant', 
                    'content': message.content,
                    'tool_calls': message.tool_calls
                })
                
                for tool_call in message.tool_calls:
                    tool_id = tool_call.id
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)  # Safely parse JSON
                    except json.JSONDecodeError:
                        tool_args = {}
                    
                    print(f"Calling tool {tool_name} with args {tool_args}")
                    
                    # Call the MCP tool
                    result = await self.session.call_tool(tool_name, arguments=tool_args)
                    
                    # Format the tool result content for OpenAI
                    if hasattr(result, 'content') and result.content:
                        if isinstance(result.content, list):
                            content_text = ""
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    content_text += content_item.text
                                elif isinstance(content_item, dict) and 'text' in content_item:
                                    content_text += content_item['text']
                                else:
                                    content_text += str(content_item)
                        else:
                            content_text = str(result.content)
                    else:
                        content_text = str(result)
                    
                    # Add tool result message
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": content_text
                    })
                
                # Get next response
                response = self.azure_openai.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"), 
                    tools=self.available_tools,
                    messages=messages,
                    max_tokens=2024
                )
                
                # Check if this is the final response
                next_message = response.choices[0].message
                if next_message.content and not next_message.tool_calls:
                    print(next_message.content)
                    process_query = False

    
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
        
                if query.lower() == 'quit':
                    break
                    
                await self.process_query(query)
                print("\n")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",  # Executable
            args=["run", "research_server.py"],  # Path to your MCP server script
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()
    
                # List available tools
                response = await session.list_tools()
                
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])
                
                self.available_tools = [{
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in response.tools]
    
                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()
  

if __name__ == "__main__":
    asyncio.run(main())
