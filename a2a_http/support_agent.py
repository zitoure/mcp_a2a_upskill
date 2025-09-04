import requests
from openai import AzureOpenAI
import json
from dotenv import load_dotenv
import os
from a2a import A2AClient

load_dotenv()

def get_azure_openai_client():
    azure_openai = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    return azure_openai

def interpret_request(user_request, openai_client):
    prompt = f"""
    Convert this user request into dict with a single key "product":
    Request: {user_request}
    
    Examples:
    "Do we have laptops?" -> {{"product": "laptop"}}
    "Check phone inventory" -> {{"product": "phone"}}
    "Any keyboards available?" -> {{"product": "keyboard"}}
    
    Respond ONLY in dict format.
    """
    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            messages=[{"role":"user","content":prompt}],
            max_tokens=100
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {content}")
        raise e
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        raise e

def request_inventory(product):
    """Request inventory information from the inventory agent"""
    return A2AClient.send_task(
        agent_url="http://127.0.0.1:9000",
        task_name="check_stock",
        params={"product": product}
    )

def interactive_mode():
    """Run in interactive mode for testing"""
    openai_client = get_azure_openai_client()
    
    print("🤖 Support Agent Interactive Mode")
    print("Ask me about inventory! Type 'quit' to exit.")
    print("-" * 40)
    
    while True:
        try:
            user_request = input("\nYou: ").strip()
            
            if user_request.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            if not user_request:
                continue
            
            print(f"🔍 Processing: {user_request}")
            
            # Parse the request using Azure OpenAI
            try:
                parsed = interpret_request(user_request, openai_client)
                print(f"📝 Understood: Looking for '{parsed.get('product')}'")
            except Exception as e:
                print(f"❌ Sorry, I couldn't understand that request: {e}")
                continue
            
            product = parsed.get("product")
            if not product:
                print("❌ I couldn't identify a product in your request")
                continue
            
            # Request inventory from the inventory agent
            print(f"📞 Checking with inventory agent...")
            result = request_inventory(product)
            
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                stock = result['stock']
                if stock > 0:
                    print(f"✅ Great news! We have {stock} {result['product']}(s) in stock")
                else:
                    print(f"📋 Sorry, {result['product']} is currently out of stock")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    print("🚀 Support Agent Starting...")
    
    # Check if inventory agent is available
    health = A2AClient.health_check("http://127.0.0.1:9000")
    if "error" in health:
        print("❌ Cannot connect to inventory agent. Make sure it's running on port 9000.")
        print("   Run: python inventory_agent.py")
        exit(1)
    else:
        print(f"✅ Connected to: {health.get('agent', 'Inventory Agent')}")
    
    # Test with a sample request first
    print("\n📋 Testing with sample request...")
    openai_client = get_azure_openai_client()
    
    user_request = "Do we have laptops in stock?"
    print(f"User request: {user_request}")
    
    # Parse the request using Azure OpenAI
    try:
        parsed = interpret_request(user_request, openai_client)
        print(f"Parsed request: {parsed}")
        
        product = parsed.get("product")
        
        # Request inventory from the inventory agent
        print(f"Checking inventory for: {product}")
        result = request_inventory(product)
        print(f"Inventory response: {result}")

        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ Stock of {result['product']}: {result['stock']} units")
    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        print("Check your Azure OpenAI configuration in .env file")
    
    # Enter interactive mode
    print("\n" + "="*50)
    interactive_mode()
