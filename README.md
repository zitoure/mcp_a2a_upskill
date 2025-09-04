# MCP and A2A Upskilling

This repository contains several small example projects used to explore MCP (Model Context Protocol) and Agent-to-Agent (A2A) interactions. The examples are intentionally simple so you can run and adapt them locally.

Top-level folders of interest

- `mcp_project/` – a minimal MCP example with a `research_server` and an interactive `mcp_chatbot` (connects to an MCP server over stdio).
- `a2a_acp/` – an ACP (Agent-to-Agent) demo showing agents and a small MCP tool server. Includes `client.py`, `mcpserver.py`, several agents (`health_agent.py`, `hospital_agent_mcp.py`, `rag_agent.py`), and example data.
- `a2a_http/` – a tiny HTTP-based A2A framework (Flask-based) in `a2a.py` with a small `A2AClient` to call other agents.
- `a2a_example/` – other A2A examples (scripts to explore agent workflows).

Quick setup

1. Create and activate a virtual environment (Windows cmd.exe):
   python -m venv .venv
   .venv\Scripts\activate

2. Install dependencies using the top-level `requirements.txt`:
   pip install -r requirements.txt

3. Create a `.env` file (if you plan to use Azure OpenAI features) in the relevant folder(s) and provide the required environment variables. Common variables used across examples:

   AZURE_OPENAI_API_KEY
   AZURE_OPENAI_ENDPOINT
   AZURE_OPENAI_DEPLOYMENT
   AZURE_OPENAI_API_VERSION

Note: many demo scripts include a fallback if Azure credentials are not set; consult the per-folder README for details.

Running the demos

- MCP demo (mcp_project):
  1. Start the research server (preferred via `uv` as some clients expect it):
     uv run mcp_project/research_server.py
     or if `uv` is not available:
     python mcp_project/research_server.py
  2. Start the chatbot client in another terminal:
     python mcp_project/mcp_chatbot.py
  The chatbot will attempt to spawn the server using `uv` if possible; otherwise start the server manually first.

- A2A ACP demo (a2a_acp):
  The `a2a_acp` folder contains an ACP (Agent-to-Agent) demo with several example agents and a small MCP tool server. The `client.py` script now provides a simple interactive menu so you can choose which workflow to run and it prints which agents must be running before invoking a workflow.

  1) Simple interactive (policy_agent only):
     - Required agent: policy_agent (RAG/policy agent running on http://localhost:8001).
     - Start it with:

       python a2a_acp/rag_agent.py

     - Then run the client and select option 1:

       python a2a_acp/client.py

     This option runs a simple prompt loop that sends your input to the policy agent.

  2) Hospital workflow (health_agent + policy_agent):
     - Required agents:
       - health_agent (runs on http://localhost:8000)
       - policy_agent (runs on http://localhost:8001)
     - Start them with:

       python a2a_acp/health_agent.py
       python a2a_acp/rag_agent.py

     - Run the client and select option 2:

       python a2a_acp/client.py

     The scripted workflow calls the health agent to get clinical context and then forwards that context to the policy agent.

  3) Doctor workflow (hospital_agent_mcp only):
     - Required agent: hospital_agent_mcp (runs on http://localhost:8000).
     - `hospital_agent_mcp.py` may spawn or expect the MCP tool server (`mcpserver.py`) as a dependency. If needed, run the MCP server separately with:

       python a2a_acp/mcpserver.py

     - Start the hospital agent and choose option 3 in the client menu:

       python a2a_acp/hospital_agent_mcp.py
       python a2a_acp/client.py

     The `hospital_agent_mcp` exposes doctor/hospital related functions and may contact the local MCP tool server to look up tools (for example `list_doctors`). The doctor workflow demonstrates calling the hospital agent and printing results.

  Note: If your agents run on non-default ports or different hosts, update the base URLs in `a2a_acp/client.py` or modify the file to accept base URLs.

- A2A HTTP demo (a2a_http):
  Use the `A2AServer` in `a2a_http/a2a.py` to register tasks and run an HTTP agent. You can also use `A2AClient` from that file to call agents over HTTP.
