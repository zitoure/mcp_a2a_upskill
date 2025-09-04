# A2A HTTP demo

This folder contains a lightweight HTTP-based Agent-to-Agent (A2A) implementation used for simple agent communication and testing.

## What is in this folder

- `a2a.py` - A small framework that provides:
  - `A2AServer` - a tiny Flask-based server you can use to register task handlers and expose simple endpoints:
    - `POST /task` - run a named task handler with a JSON payload: {"task": "task_name", "params": {...}}
    - `GET /health` - health check
    - `GET /info` - agent metadata and available tasks
  - `A2AClient` - a helper class with `send_task`, `get_agent_info`, and `health_check` methods (uses `requests`).

This folder also includes two small demo agents:

- `inventory_agent.py` - A minimal inventory service that exposes tasks such as `check_stock`, `list_products`, and `update_stock`. It runs an `A2AServer` on `http://127.0.0.1:9000` and accepts `POST /task` requests for inventory queries.

- `support_agent.py` - A support front-end agent that interprets user requests (using Azure OpenAI) and queries the `inventory_agent` to answer inventory questions. The support agent performs a health check on the inventory agent at startup and will prompt you to start it if it is not available.

## Prerequisites

- Python 3.8+
- Create and activate a virtual environment (recommended)
  - Windows (cmd.exe):

    ```cmd
    python -m venv .venv
    .venv\Scripts\activate
    ```

- Install dependencies (you can use the top-level `requirements.txt` if present):

    ```bash
    pip install Flask requests python-dotenv
    ```

## Running the demo agents (inventory / support)

1. Start the inventory agent in one terminal (it listens on `http://127.0.0.1:9000`):

    ```cmd
    python inventory_agent.py
    ```

   The inventory agent exposes:
   - `GET /health` – health check
   - `GET /info` – agent metadata and available tasks
   - `POST /task` – run a named task (e.g., `check_stock`, `list_products`)

2. Start the support agent in a separate terminal. The support agent performs a health check against the inventory agent on startup and will refuse to run if the inventory agent is not reachable.

    ```cmd
    python support_agent.py
    ```

   The support agent also uses Azure OpenAI to interpret natural language requests. If you want that feature to work, create a `.env` file or set the following environment variables in your shell:

   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT_NAME` (optional, defaults to `gpt-4o-mini`)

   If Azure credentials are not set, the interpretation feature will raise errors; you can still query the inventory agent directly.

