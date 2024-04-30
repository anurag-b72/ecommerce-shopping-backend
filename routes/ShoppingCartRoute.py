from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config.db import *
from bson import ObjectId

shoppingCartRouter = APIRouter()

@shoppingCartRouter.post("/user/cart/add-items", tags=["Cart APIs"])
async def add_items(user_id: str, product_id: str, quantity: int):
    """
    This asynchronous function adds items to a user's shopping cart via a POST request at the /user/cart/add-items endpoint. It first verifies the existence of the user and the product in their respective MongoDB collections (user_collection and product_collection). If both the user and the product exist, it either updates the quantity of an existing item in the cart or adds a new item if it is not already in the cart.

Parameters:
- user_id (str): The MongoDB _id of the user whose cart is being updated.
- product_id (str): The MongoDB _id of the product to add to the cart.
- quantity (int): The quantity of the product to be added to the cart.

Returns:
- dict: A dictionary containing a message about the operation's success, either confirming the addition of a new product or the update of an existing one in the cart.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code in two cases:
    - If no user is found with the given user_id.
    - If no product is found with the given product_id.

    """
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

@shoppingCartRouter.put("/user/cart/update-quantity", tags=["Cart APIs"])
async def update_cart_item_quantity(user_id: str, product_id: str, new_quantity: int):
    """
    This asynchronous function is designed to update the quantity of a specific item in a user's shopping cart via a PUT request at the /user/cart/update-quantity endpoint. It verifies the existence of both the user and the specified product within the user's cart. If the product is found, it updates the quantity; if not, it raises an HTTP exception.

Parameters:
- user_id (str): The MongoDB _id of the user whose cart is to be updated.
- product_id (str): The MongoDB _id of the product in the cart whose quantity needs updating.
- new_quantity (int): The new quantity to set for the product in the cart.

Returns:
- dict: A dictionary containing a message indicating the successful update of the product quantity within the user's cart.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code in two cases:
    - If no user is found with the given user_id.
    - If the specified product is not found in the user's shopping cart.

    """
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
    """
    This asynchronous function facilitates the removal of an item from a user's shopping cart via a DELETE request at the /user/cart/remove-item endpoint. It first verifies the existence of the user in the user_collection of a MongoDB database. If the user exists, it then checks for the product in the user's shopping cart. If found, the product is removed from the cart; if not, an HTTP exception is raised.

Parameters:
- user_id (str): The MongoDB _id of the user whose cart is being modified.
- product_id (str): The MongoDB _id of the product to be removed from the cart.

Returns:
- dict: A dictionary containing a message indicating the successful removal of the product from the user's shopping cart.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code in two cases:
    - If no user is found with the given user_id.
    - If the specified product is not found in the user's shopping cart.

    """
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

@shoppingCartRouter.get("/user/cart/get-items", tags=["Cart APIs"])
async def get_user_cart(user_id: str):
    """
    This asynchronous function retrieves the contents of a user's shopping cart via a GET request at the /user/cart/get-items endpoint. It first confirms the existence of the user in the user_collection of a MongoDB database. If the user exists, it retrieves the items in the user's shopping cart. If the user does not exist, it raises an HTTP exception.

Parameters:
- user_id (str): The MongoDB _id of the user whose shopping cart items are being retrieved.

Returns:
- dict: A dictionary containing the user's _id and a list of items in the shopping cart. Each item in the list typically includes product identifiers and quantities.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code if no user is found with the specified user_id.

    """
    # Check if the user exists in the user_collection
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the shopping cart items from the user document
    shopping_cart = user.get("shopping_cart", [])
    
    return {"user_id": user_id, "shopping_cart": shopping_cart}

@shoppingCartRouter.get("/user/cart/total-price", tags=["Cart APIs"])
async def calculate_total_price(user_id: str):
    """
    This asynchronous function calculates the total price of all items in a user's shopping cart via a GET request at the /user/cart/total-price endpoint. It verifies the existence of the user in the user_collection of a MongoDB database and then aggregates the total cost based on product details fetched from the product_collection.

Parameters:
- user_id (str): The MongoDB _id of the user whose cart's total price is being calculated.

Returns:
- dict: A dictionary containing the user's _id and the calculated total price of the items in their shopping cart. The price is computed by multiplying each product's price by its quantity in the cart.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code if no user is found with the specified user_id.

    """
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