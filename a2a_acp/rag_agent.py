from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server

from crewai import Crew, Task, Agent, LLM
from crewai_tools import RagTool
from langchain_openai import AzureChatOpenAI
import openai
import nest_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

nest_asyncio.apply()

server = Server()

# Validate required environment variables
def validate_azure_config():
    """Validate that all required Azure OpenAI environment variables are set"""
    required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    print("✅ Azure OpenAI configuration validated")
    print(f"   Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"   API Key: {os.getenv('AZURE_OPENAI_API_KEY')[:8]}...")
    print(f"   Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')}")

# Validate configuration first
validate_azure_config()

# Remove conflicting OpenAI key and set proper Azure environment variables
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]

# Set comprehensive Azure environment variables for all components
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")  # LiteLLM expects this for Azure
os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Also set Azure-specific environment variables
os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["AZURE_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
os.environ["AZURE_API_TYPE"] = "azure"

def setup_rag_tool():
    """Setup RAG tool with simplified configuration"""
    
    try:
        print("🔧 Initializing RAG tool with minimal config...")
        config = {
            "llm": {
                "provider": "openai",  # Try openai provider with Azure format
                "config": {
                    "model": f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')}",
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": f"azure/{os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-ada-002')}",
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                    "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    }
            }
        }
        
        rag_tool = RagTool(config=config, chunk_size=1200, chunk_overlap=200)
        rag_tool.add("gold_hospital.pdf", data_type="pdf_file")
        print("✅ RAG tool initialized with alternative config")
        return rag_tool, True
        
    except Exception as e2:
        print(f"❌ Alternative config also failed: {e2}")
        print("🔄 Continuing without RAG capabilities")
        return None, False

rag_tool, RAG_AVAILABLE = setup_rag_tool()

def setup_llm():
    """Setup LLM with complete Azure configuration"""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    
    # Set environment variables for LiteLLM Azure support
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = endpoint
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_VERSION"] = api_version
    
    # Use CrewAI's LLM class with proper Azure configuration
    return LLM(
        model=f"azure/{deployment}",  # Azure format for LiteLLM
        api_key=api_key,
        base_url=endpoint,
        temperature=0.5,
        max_tokens=1000,
        extra_headers={
            "api-key": api_key
        }
    )

llm = setup_llm()

@server.agent()
async def policy_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This is an agent for questions around policy coverage, it uses a RAG pattern to find answers based on policy documentation. Use it to help answer questions on coverage and waiting periods."""

    # Ensure Azure environment is properly set for this request
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Also set Azure-specific variables
    os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["AZURE_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ["AZURE_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    tools = []
    if RAG_AVAILABLE and rag_tool:
        tools.append(rag_tool)
        backstory = "You are an expert insurance agent designed to assist with coverage queries. Use the RAG tool to search through policy documentation to provide accurate answers."
    else:
        backstory = "You are an expert insurance agent designed to assist with coverage queries. Provide helpful answers based on general insurance knowledge."

    insurance_agent = Agent(
        role="Senior Insurance Coverage Assistant", 
        goal="Determine whether something is covered or not",
        backstory=backstory,
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=tools, 
        max_retry_limit=3
    )
    
    task1 = Task(
         description=input[0].parts[0].content,
         expected_output="A comprehensive response to the user's question about insurance coverage",
         agent=insurance_agent
    )
    
    crew = Crew(agents=[insurance_agent], tasks=[task1], verbose=True)
    
    try:
        task_output = await crew.kickoff_async()
        yield Message(parts=[MessagePart(content=str(task_output))])
    except Exception as e:
        print(f"❌ Error in policy_agent: {e}")
        error_message = f"I apologize, but I encountered an error while processing your request. Please try again. Error details: {str(e)}"
        yield Message(parts=[MessagePart(content=error_message)])

if __name__ == "__main__":
    print("🚀 Starting RAG Agent Server on port 8001...")
    print(f"📚 RAG Available: {RAG_AVAILABLE}")
    
    # Print configuration for debugging
    print("\n🔍 Configuration Check:")
    print(f"   AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"   AZURE_OPENAI_API_KEY: {'✅ Set' if os.getenv('AZURE_OPENAI_API_KEY') else '❌ Missing'}")
    print(f"   AZURE_OPENAI_DEPLOYMENT: {os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')}")
    print(f"   AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')}")
    
    server.run(port=8001)