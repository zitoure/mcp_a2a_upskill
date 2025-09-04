# MCP Project

This folder contains a small example of how to make and connect to an MCP (Model Context Protocol) server project used in the DEEPLEARNING.AI MCP course. Below is a short description of what is in this folder and simple instructions for running the components.

## What is in this folder

- `mcp_chatbot.py` - A simple client/chat application that connects to an MCP server over stdio. It uses Azure OpenAI (via environment variables) and will call tools exposed by the server.
- `research_server.py` - An MCP server that exposes research-related tools (for example, a `search_papers` tool that queries arXiv and saves results under the `papers/` directory).
- `papers/` - A directory where `research_server.py` saves JSON files with paper metadata (e.g., `papers/<topic>/papers_info.json`).

## Prerequisites

- Python 3.8+ (project files indicate Python 3.11 artifacts but 3.8+ should work)
- Create and activate a virtual environment (recommended):
  - Windows (cmd.exe):
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
- Install dependencies:
  - If there is a `requirements.txt` in the workspace, use it. Otherwise install the packages used by the scripts:
    ```bash
    pip install python-dotenv openai arxiv nest_asyncio mcp
    ```

## Environment variables

- `mcp_chatbot.py` uses Azure OpenAI via environment variables. Create a `.env` file in this folder or set the variables in your environment with values appropriate for your Azure/OpenAI setup. Example `.env`:

  ```env
  AZURE_OPENAI_API_KEY=your_api_key_here
  AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
  AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
  AZURE_OPENAI_API_VERSION=2024-02-15-preview
  ```

## How to run

1. **Start the research server (tool provider)**

   Open a terminal and from this folder run:

   ```bash
   python research_server.py
   ```

   This will start the MCP server and register the research tools. When you run `search_papers(...)` via the tool, results will be saved in `papers/<topic>/papers_info.json`.

2. **Run the chatbot client (tool consumer)**

   Open a second terminal, make sure your virtualenv is activated and environment variables are set, then run:

   ```bash
   python mcp_chatbot.py
   ```

    The chatbot will connect over stdio and present an interactive prompt where you can type queries. Type `quit` to exit.


