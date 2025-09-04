# ACP client to interact with agents
import nest_asyncio
from acp_sdk.client import Client
import asyncio
from colorama import Fore, Style, init

init()
nest_asyncio.apply()

async def run_doctor_workflow() -> None:
    async with Client(base_url="http://localhost:8000") as hospital:
        run1 = await hospital.run_sync(
            agent="doctor_agent", input="I'm based in Atlanta,GA. Are there any Cardiologists near me?"
        )
        content = run1.output[0].parts[0].content
        print(Fore.LIGHTMAGENTA_EX+ content + Fore.RESET)

async def run_hospital_workflow() -> None:
    """ This workflow simulates a hospital agent and policy agent interaction."""
    async with Client(base_url="http://localhost:8001") as insurer, Client(base_url="http://localhost:8000") as hospital:
        run1 = await hospital.run_sync(
            agent="health_agent", input="Do I need rehabilitation after a shoulder reconstruction?"
        )
        content = run1.output[0].parts[0].content
        print(Fore.LIGHTMAGENTA_EX+ content + Fore.RESET)

        run2 = await insurer.run_sync(
            agent="policy_agent", input=f"Context: {content} What is the waiting period for rehabilitation?"
        )
        print(Fore.YELLOW + run2.output[0].parts[0].content + Fore.RESET)

async def simple_interactive():
    """Simple interactive client. this allows users to interact with the policy agent."""
    print("🚀 A2A Interactive Client - Type 'quit' to exit")
    
    async with Client(base_url="http://localhost:8001") as client:
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                break
                
            if user_input:
                try:
                    run = await client.run_sync(
                        agent="policy_agent", 
                        input=user_input
                    )
                    response = run.output[0].parts[0].content
                    print(f"Agent: {response}")
                except Exception as e:
                    print(f"Error: {str(e)}")

# Add a simple menu to let the user pick a workflow and show required agents
async def main_menu():
    menu = (
        "\nSelect a workflow to run:\n"
        "1) Simple interactive (policy_agent only)\n"
        "2) Hospital workflow (health_agent + policy_agent)\n"
        "3) Doctor workflow (hospital_agent_mcp only)\n"
        "4) Quit\n"
        "Enter choice [1-4]: "
    )

    while True:
        choice = input(menu).strip()

        if choice == '1':
            print("\n[Prerequisite] Ensure the policy agent (policy_agent) is running on http://localhost:8001. You can start it with: python rag_agent.py")
            print("Starting simple interactive client (policy_agent)...\n")
            await simple_interactive()

        elif choice == '2':
            print("\n[Prerequisites] Ensure the following agents are running:")
            print("  - health_agent on http://localhost:8000 (run health_agent.py)")
            print("  - policy_agent on http://localhost:8001 (run rag_agent.py)")
            input("Press Enter when the required agents are running and reachable...")
            print("\nRunning hospital workflow (health_agent + policy_agent)...\n")
            try:
                await run_hospital_workflow()
            except Exception as e:
                print(f"Error running hospital workflow: {e}")

        elif choice == '3':
            print("\n[Prerequisite] Ensure the hospital agent (hospital_agent_mcp) is running on http://localhost:8000. This agent logs and may spawn the mcpserver automatically (run hospital_agent_mcp.py)")
            input("Press Enter when the required agent is running and reachable...")
            print("\nRunning doctor workflow (hospital_agent_mcp)...\n")
            try:
                await run_doctor_workflow()
            except Exception as e:
                print(f"Error running doctor workflow: {e}")

        elif choice in ['4', 'q', 'quit', 'exit']:
            print("Goodbye")
            break

        else:
            print("Invalid selection. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    asyncio.run(main_menu())