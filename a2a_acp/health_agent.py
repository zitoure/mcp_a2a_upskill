from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from smolagents import CodeAgent, DuckDuckGoSearchTool, OpenAIServerModel, VisitWebpageTool
import logging 
import os
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv() 

server = Server()

class AzureOpenAIServerModel(OpenAIServerModel):
    """This model connects to an Azure OpenAI deployment.

    Parameters:
        model_id (`str`):
            The model identifier to use on the server (e.g. "gpt-3.5-turbo").
        azure_endpoint (`str`, *optional*):
            The Azure endpoint, including the resource, e.g. `https://example-resource.azure.openai.com/`
        api_key (`str`, *optional*):
            The API key to use for authentication.
        custom_role_conversions (`Dict{str, str]`, *optional*):
            Custom role conversion mapping to convert message roles in others.
            Useful for specific models that do not support specific message roles like "system".
        **kwargs:
            Additional keyword arguments to pass to the Azure OpenAI API.
    """

    def __init__(
        self,
        model_id: str,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        custom_role_conversions: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(model_id=model_id, api_key=api_key, custom_role_conversions=custom_role_conversions, **kwargs)
        # if we've reached this point, it means the openai package is available (baseclass check) so go ahead and import it
        import openai

        self.client = openai.AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )

model = AzureOpenAIServerModel(
    model_id = "gpt-4o-mini",
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
)

@server.agent()
async def health_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    "This is a CodeAgent which supports the hospital to handle health based questions for patients. Current or prospective patients can use it to find answers about their health and hospital treatments."
    agent = CodeAgent(tools=[DuckDuckGoSearchTool(), VisitWebpageTool()], model=model)

    prompt = input[0].parts[0].content
    response = agent.run(prompt)

    yield Message(parts=[MessagePart(content=str(response))])


if __name__ == "__main__":
    server.run(port=8000)
