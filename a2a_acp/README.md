A2A ACP demo

This folder contains a small demo of an ACP-based (Agent-to-Agent) workflow. The code is adapted from the DEEPLEARNING.IA course on ACP protocol

What is in this folder

- `client.py` - A simple interactive client and a scripted workflow (`run_hospital_workflow`) that demonstrates interactions with a hospital agent and a policy agent. By default running the file (`python client.py`) will start an interactive prompt where you can send inputs to the `policy_agent`.
- `mcpserver.py` - An MCP tool server exposing a `list_doctors` tool; this illustrates how MCP tools can be implemented and published over stdio.
- `health_agent.py`, `hospital_agent_mcp.py`, `rag_agent.py` - Example agent implementations used by the demo.
- `db/chroma.sqlite3` - Example local database used by the demo (if present).
- `gold_hospital.pdf` - Example/reference document included in the repo.

Prerequisites

- Python 3.8+
- A virtual environment is recommended. On Windows (cmd.exe):
  python -m venv .venv
  .venv\Scripts\activate

- Install dependencies (you can use the top-level `requirements.txt` if present):
  pip install acp-sdk colorama nest_asyncio mcp requests

How to run

1) Which agents you need to run

- Simple interactive client (default option 1 in `client.py`):
  - Requires only the policy agent to be running (policy_agent).
  - The policy agent in this demo is provided by `rag_agent.py` and listens on http://localhost:8001 by default. To start it, run:

    python rag_agent.py

- Hospital workflow (option 2 in `client.py`):
  - Requires both `health_agent` and `policy_agent` to be running.
  - Start the health agent (runs on http://localhost:8000):

    python health_agent.py

  - Start the policy agent (runs on http://localhost:8001):

    python rag_agent.py

- Doctor workflow (option 3 in `client.py`):
  - Requires only the hospital agent (hospital_agent_mcp).
  - `hospital_agent_mcp.py` may spawn the MCP tool server (mcpserver) automatically or expect it to be available locally. To start it manually, run:

    python hospital_agent_mcp.py

  - If the tool server is needed separately, start it with:

    python mcpserver.py

2) Run the client

- From this directory run:

  python client.py

- The client now presents a simple menu allowing you to choose between: simple interactive (policy agent), hospital workflow (health_agent + policy_agent), or doctor workflow (hospital_agent_mcp).

3) Run the scripted hospital workflow (optional)

- If you want to run the scripted demo that calls both a hospital agent and an insurer/policy agent directly from Python (without the interactive menu), you can run it from Python directly. Example (from this directory):

  python -c "import asyncio; from client import run_hospital_workflow; asyncio.run(run_hospital_workflow())"

Notes and troubleshooting

- The client expects ACP services (agents) to be available at the configured base URLs (see `client.py`). If your ACP runtime uses different ports, update the `base_url` values there.
- If the MCP chatbot/client attempts to spawn a server with `uv` and it's not available, start the server manually using `python mcpserver.py`.
- If you rely on local data (e.g., `db/chroma.sqlite3`), ensure the file is present and with the expected contents/permissions.

Agent Details

- `health_agent.py` - A CodeAgent that answers health-related questions. It uses an Azure OpenAI model (wrapped in a small Azure-compatible model class), and includes tools for web search and webpage visiting (DuckDuckGoSearchTool and VisitWebpageTool). When run directly this agent starts a server on port `8000` and yields responses based on the provided prompt.

- `hospital_agent_mcp.py` - A more advanced hospital/server file that exposes multiple agents (e.g., a `health_agent` and a `doctor_agent`). It also demonstrates how to call remote MCP tools by building a `ToolCollection` from another MCP server (it configures `StdioServerParameters` to run the `mcpserver.py` tool provider using `uv run mcpserver.py`). This file also runs its server on port `8000` when executed.

- `rag_agent.py` - A RAG (Retrieval-Augmented Generation) / policy agent that provides insurance and coverage-related answers. It validates and configures Azure OpenAI environment variables, sets up an LLM via CrewAI, and attempts to initialize a RagTool (which ingests `gold_hospital.pdf` for retrieval). It exposes a `policy_agent` that uses CrewAI/Crew tasks to answer policy questions. When executed as a script it starts a server on port `8001`. The RAG capability is optional and guarded by the `RAG_AVAILABLE` flag — if RAG initialization fails the agent still runs in a degraded, non-RAG mode.

If you want, I can:
- Add a `requirements.txt` inside this folder with pinned versions.
- Add an example `.env` or a small script to create a virtualenv and install dependencies.
- Modify the client to accept base URLs via environment variables or command-line args.
