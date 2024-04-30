from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from models.OrderModel import OrderModel
from config.db import *
from schemas.order_schema import *
from bson import ObjectId

orderRoute = APIRouter()


# Create an endpoint to handle the purchase request
@orderRoute.post("/order/complete-purchase", tags=["Shopping Order APIs"])
async def complete_purchase(user_id, user_address):
    """
    This asynchronous function facilitates the completion of a purchase through a POST request at the /order/complete-purchase endpoint. It interacts with MongoDB collections (user_collection, product_collection, order_collection) to fetch user details, calculate total prices based on shopping cart contents, and save order details.


Parameters:
- user_id (str): The MongoDB _id of the user making the purchase. This identifier is used to fetch the user's details and shopping cart.
- user_address (str): The address provided by the user for order delivery.

Returns:
- dict: A dictionary containing a message indicating successful completion of the purchase and the order_id of the newly created order.

Raises:
- HTTPException: This function raises an HTTP exception in two cases:
If a product in the shopping cart does not exist in the product_collection (404 status code with a detailed error message).
If there is no user matching the provided user_id in the user_collection (implicitly, if user is None).
    """
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    
    # Calculate the total price
    total_price = 0
    
    # Iterate through items in the user's shopping cart
    for item in user.get("shopping_cart", []):
        product = product_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            total_price += product.get("price", 0) * item["quantity"]
        else:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found")

    # Save the order details in the database
    order_doc = order_collection.insert_one({
        "user_id": user_id,
        "user_address": user_address,
        "user_phone": user['phone'],
        "shopping_cart": [{"product_id": item['product_id'], "quantity": item['quantity']} for item in user['shopping_cart']],
        "total_price": total_price,
        "purchase_time": datetime.now(),
        "order_approval_status": "Pending",
    })

    # Return a response indicating successful completion of the purchase
    return {"message": "Purchase completed successfully", "order_id": str(order_doc.inserted_id)}



@orderRoute.get("/order/get-order/{order_id}", tags=["Shopping Order APIs"])
async def get_order(order_id: str):
    # Find the order in MongoDB
    order = order_collection.find_one({"_id": ObjectId(order_id)})
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return individual_serial(order)



@orderRoute.get("/order/get-all-orders", tags=["Shopping Order APIs"])
async def get_all_orders():
    # Fetch all orders from MongoDB
    orders = order_collection.find()
    return list_serial(orders)