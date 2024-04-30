from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config.db import *
from bson import ObjectId

shoppingCartRouter = APIRouter()

@shoppingCartRouter.post("/user/cart/add-items", tags=["Cart APIs"])
async def add_items(user_id: str, product_id: str, quantity: int):
    # Check if the user exists in the user_collection
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the product exists in the product_collection
    product = product_collection.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Construct the cart item
    cart_item = {"product_id": product_id, "quantity": quantity}
    
    # Check if the product is already in the user's shopping cart
    for item in user.get("shopping_cart", []):
        if item["product_id"] == product_id:
            # Add the new quantity to the previous one
            item["quantity"] += quantity
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"shopping_cart": user["shopping_cart"]}}
            )
            return {"message": f"Item already added, hence updated the quantity to {item['quantity']}"}
    
    # If the product is not already in the cart, add it
    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"shopping_cart": cart_item}}
    )
    
    return {"message": "Product added to user's shopping cart successfully"}

@shoppingCartRouter.get("/user/cart/get-items", tags=["Cart APIs"])
async def get_user_cart(user_id: str):
    # Check if the user exists in the user_collection
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the shopping cart items from the user document
    shopping_cart = user.get("shopping_cart", [])
    
    return {"user_id": user_id, "shopping_cart": shopping_cart}

@shoppingCartRouter.put("/user/cart/update-quantity", tags=["Cart APIs"])
async def update_cart_item_quantity(user_id: str, product_id: str, new_quantity: int):
    # Check if the user exists in the user_collection
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the product is in the user's shopping cart
    for item in user.get("shopping_cart", []):
        if item["product_id"] == product_id:
            # Update the quantity of the item
            item["quantity"] = new_quantity
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"shopping_cart": user["shopping_cart"]}}
            )
            return {"message": f"Quantity of item {product_id} updated successfully to {new_quantity}"}
    
    # If the product is not found in the cart, raise an error
    raise HTTPException(status_code=404, detail="Product not found in the user's shopping cart")

@shoppingCartRouter.delete("/user/cart/remove-item", tags=["Cart APIs"])
async def remove_cart_item(user_id: str, product_id: str):
    # Check if the user exists in the user_collection
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the product is in the user's shopping cart
    for index, item in enumerate(user.get("shopping_cart", [])):
        if item["product_id"] == product_id:
            # Remove the item from the shopping cart
            del user["shopping_cart"][index]
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"shopping_cart": user["shopping_cart"]}}
            )
            return {"message": f"Item {product_id} removed from the shopping cart successfully"}
    
    # If the product is not found in the cart, raise an error
    raise HTTPException(status_code=404, detail="Product not found in the user's shopping cart")

@shoppingCartRouter.get("/user/cart/total-price", tags=["Cart APIs"])
async def calculate_total_price(user_id: str):
    # Check if the user exists in the user_collection
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Initialize total price
    total_price = 0
    
    # Iterate through items in the user's shopping cart
    for item in user.get("shopping_cart", []):
        # Get the product details from the product_collection
        product = product_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            # Calculate the price for the current item and add it to the total price
            total_price += product.get("price", 0) * item["quantity"]
    
    return {"user_id": user_id, "total_price": total_price}