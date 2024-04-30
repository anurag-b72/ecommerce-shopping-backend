from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from models.AdminModel import Admin
from config.db import *
from schemas.user_schema import *
from typing import Literal
from bson import ObjectId

adminRouter = APIRouter()  

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#POST Request Method
@adminRouter.post("/admin/admin-register", tags=["Admin APIs"])
async def admin_register(admin: Admin):
    """
    This asynchronous function handles the registration of new admin users via a POST request at the endpoint /admin/admin-register. It uses a MongoDB collection admin_collection to manage admin data. The function first checks if the given admin's username already exists in the database to prevent duplicate registrations. If the username exists, it raises an HTTP exception. Otherwise, it hashes the admin's password for secure storage and inserts the new admin record into the database.

Parameters:
- admin (Admin): An object representing the admin to be registered. The object must have at least admin_username and admin_password attributes.

Returns:
- JSONResponse: A JSON response indicating the result of the registration process. It returns a 201 status code with a success message and the MongoDB inserted_id of the new admin if registration is successful.

Raises:
- HTTPException: If an admin with the given username already exists, it raises an HTTPException with a 400 status code and a detail message "Admin already exists!".
    """
    adminPresent = admin_collection.find_one({"admin_username": admin.admin_username})  # Check if username is already registered
    if adminPresent:
        raise HTTPException(status_code=400, detail="Admin already exists!")
    
    hashed_password = pwd_context.hash(admin.admin_password)
    admin.admin_password = hashed_password  # Store the hashed password instead of the plain one
    res = admin_collection.insert_one(dict(admin))
    return JSONResponse(status_code=201, content={"message": "New Admin Created.", "admin_id": str(res.inserted_id)})


#GET Request Method
@adminRouter.get("/admin/admin-login", tags=["Admin APIs"])
async def admin_login(username: str, password: str):
    """
    This asynchronous function handles the login of admin users via a GET request at the endpoint /admin/admin-login. It uses the admin_collection from a MongoDB database to verify admin credentials. The function first checks if the admin with the specified username exists. If the admin exists and the password is correct, it confirms the login and returns a success message. If the password is incorrect, or the username does not exist, it raises an HTTP exception.

Parameters:
- username (str): The username of the admin attempting to log in.
- password (str): The password provided by the admin for login.

Returns:
- dict: A dictionary containing a success message if login is successful, including a welcome message using the admin's first name from the database.

Raises:
- HTTPException: This function raises an HTTP exception with a 400 status code under two conditions:
If the password provided is incorrect.
If there is no admin with the specified username.
    """
    adminPresent = admin_collection.find_one({"admin_username": username})
    if adminPresent:
        if pwd_context.verify(password, adminPresent["admin_password"]):
            return {"message": "Logged In Successfully!, Welcome " + adminPresent["admin_first_name"], "admin_id": str(adminPresent['_id'])}
        else:
            raise HTTPException(status_code=400, detail="Wrong Password!")
    else:
        raise HTTPException(status_code=400, detail="Wrong Phone or Password")



#GET Request Method
@adminRouter.get("/admin/get-all-users", tags=["Admin APIs"])
async def get_all_users():
    """
    This asynchronous endpoint retrieves all users from the user collection. It is mapped to the HTTP GET method at the route /admin/get-all-users. This function forms part of the "Admin APIs" operations as indicated by its route tag.

Returns:
- list of dict: Returns a serialized list of user documents if any exist.
- HTTPException: Raises an HTTP 404 exception if no users are found in the collection.

Raises:
- HTTPException: If no users are registered in the system, this exception is thrown with a status code of 404 and a detail message "No user registered in the system!"

    """
    users = user_collection.find()
    if users:
        return list_serial(users)
    else:
        raise HTTPException(status_code=404, detail="No user registered in the system!")

#GET Request Method
@adminRouter.get("/admin/order-management", tags=["Admin APIs"])
async def order_management(order_id: str, admin_id: str,  order_action: Literal["approve", "reject"]):
    order = order_collection.find_one({"_id": ObjectId(order_id)})
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    
    admin = admin_collection.find_one({"_id": ObjectId(admin_id)})
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not registered.")
    
    if order_action == 'approve':
        order_collection.find_one_and_update(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "order_approval_status": "Approved"
            }}
        )
        return {"message": "Order status approved by admin id=" + admin_id}
    
    else:
        order_collection.find_one_and_update(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "order_approval_status": "Rejected"
            }}
        )
        return {"message": "Order status rejected by admin id=" + admin_id}
        
    # if users:
    #     return list_serial(users)
    # else:
    #     raise HTTPException(status_code=404, detail="No user registered in the system!")