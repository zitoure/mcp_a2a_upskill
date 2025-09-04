from a2a import A2AServer

# Sample inventory data
inventory_data = {
    "laptop": 12,
    "phone": 5,
    "keyboard": 0,
    "mouse": 8,
    "monitor": 3,
    "tablet": 7
}

server = A2AServer(
    agent_name="InventoryAgent", 
    description="Manages and responds to inventory stock queries"
)

@server.register_task_handler("check_stock")
async def check_stock(params):
    """Check stock level for a specific product"""
    product = params.get("product", "").lower().strip()
    
    if not product:
        return {"error": "Product parameter is required"}
    
    # Check if product exists in inventory
    stock_level = inventory_data.get(product)
    
    if stock_level is None:
        available_products = list(inventory_data.keys())
        return {
            "error": f"Product '{product}' not found. Available products: {', '.join(available_products)}"
        }
    
    return {
        "product": product,
        "stock": stock_level,
        "status": "in_stock" if stock_level > 0 else "out_of_stock"
    }

@server.register_task_handler("list_products")
async def list_products(params):
    """List all available products and their stock levels"""
    return {
        "products": inventory_data,
        "total_items": sum(inventory_data.values()),
        "total_products": len(inventory_data)
    }

@server.register_task_handler("update_stock")
async def update_stock(params):
    """Update stock level for a product (for demo purposes)"""
    product = params.get("product", "").lower().strip()
    quantity = params.get("quantity")
    
    if not product:
        return {"error": "Product parameter is required"}
    
    if quantity is None:
        return {"error": "Quantity parameter is required"}
    
    try:
        quantity = int(quantity)
    except ValueError:
        return {"error": "Quantity must be a number"}
    
    if product not in inventory_data:
        return {"error": f"Product '{product}' not found"}
    
    old_stock = inventory_data[product]
    inventory_data[product] = max(0, quantity)  # Don't allow negative stock
    
    return {
        "product": product,
        "old_stock": old_stock,
        "new_stock": inventory_data[product],
        "message": f"Updated {product} stock from {old_stock} to {inventory_data[product]}"
    }

if __name__ == "__main__":
    print("🏪 Starting Inventory Agent...")
    print(f"📦 Managing {len(inventory_data)} products:")
    for product, stock in inventory_data.items():
        status = "✅" if stock > 0 else "❌"
        print(f"   {status} {product}: {stock}")
    
    print("\n🚀 Server starting on http://127.0.0.1:9000")
    print("📋 Available tasks:")
    print("   • check_stock - Check stock for a product")
    print("   • list_products - List all products")
    print("   • update_stock - Update stock level")
    print("\n💡 Test endpoints:")
    print("   • GET  http://127.0.0.1:9000/health")
    print("   • GET  http://127.0.0.1:9000/info")
    print("   • POST http://127.0.0.1:9000/task")
    
    server.run(host="127.0.0.1", port=9000)