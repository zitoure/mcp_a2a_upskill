"""
Simple Agent-to-Agent (A2A) Communication Framework
This provides a basic HTTP-based agent communication system.
"""
import asyncio
from flask import Flask, request, jsonify
from typing import Callable, Dict, Any

class A2AServer:
    def __init__(self, agent_name: str, description: str = ""):
        self.agent_name = agent_name
        self.description = description
        self.app = Flask(__name__)
        self.task_handlers: Dict[str, Callable] = {}
        
        # Register default routes
        self.app.route('/task', methods=['POST'])(self._handle_task)
        self.app.route('/health', methods=['GET'])(self._health_check)
        self.app.route('/info', methods=['GET'])(self._agent_info)
    
    def register_task_handler(self, task_name: str):
        """Decorator to register a task handler"""
        def decorator(func: Callable):
            self.task_handlers[task_name] = func
            return func
        return decorator
    
    def _handle_task(self):
        """Handle incoming task requests"""
        try:
            data = request.get_json()
            task_name = data.get('task')
            params = data.get('params', {})
            
            if task_name not in self.task_handlers:
                return jsonify({"error": f"Task '{task_name}' not found"}), 400
            
            # Execute the task handler
            handler = self.task_handlers[task_name]
            
            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                # Run async handler in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(handler(params))
                finally:
                    loop.close()
            else:
                result = handler(params)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def _health_check(self):
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "agent": self.agent_name,
            "description": self.description
        })
    
    def _agent_info(self):
        """Agent information endpoint"""
        return jsonify({
            "agent_name": self.agent_name,
            "description": self.description,
            "available_tasks": list(self.task_handlers.keys())
        })
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, debug: bool = False):
        """Run the agent server"""
        print(f"🚀 Starting {self.agent_name} on {host}:{port}")
        print(f"📝 Description: {self.description}")
        print(f"🔧 Available tasks: {list(self.task_handlers.keys())}")
        
        self.app.run(host=host, port=port, debug=debug)

class A2AClient:
    """Client for communicating with other A2A agents"""
    
    @staticmethod
    def send_task(agent_url: str, task_name: str, params: Dict[str, Any] = None):
        """Send a task to another agent"""
        import requests
        
        if params is None:
            params = {}
        
        payload = {
            "task": task_name,
            "params": params
        }
        
        try:
            response = requests.post(f"{agent_url}/task", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to communicate with agent: {str(e)}"}
    
    @staticmethod
    def get_agent_info(agent_url: str):
        """Get information about an agent"""
        import requests
        
        try:
            response = requests.get(f"{agent_url}/info")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to get agent info: {str(e)}"}
    
    @staticmethod
    def health_check(agent_url: str):
        """Check if an agent is healthy"""
        import requests
        
        try:
            response = requests.get(f"{agent_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Agent health check failed: {str(e)}"}
