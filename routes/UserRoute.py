from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
import shutil
import cloudinary
import cloudinary.uploader
import os
from pymongo import ReturnDocument

from models.UserModel import UserModel
from config.db import *
from schemas.user_schema import *
from bson import ObjectId
from typing import Optional

userRouter = APIRouter()  

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



#POST Request Method
@userRouter.post("/user/user-register", tags=["User APIs"])
async def user_register(user: UserModel):
    """
    This asynchronous function handles the registration of new users via a POST request at the endpoint /user/user-register. It interacts with a MongoDB collection named user_collection to manage user data. The function first verifies whether the user's phone number is already registered and checks that the phone number is exactly 10 digits long. If these conditions are met, it hashes the user's password for secure storage and then inserts the new user record into the database.

Parameters:
- user (UserModel): An object representing the user to be registered. This object should include attributes like phone and password, and possibly shopping_cart, which will be excluded from the registration record.

Returns:
- JSONResponse: A response in JSON format indicating the result of the registration process. It includes a 201 status code with a message of success and the MongoDB inserted_id of the newly registered user.

Raises:
- HTTPException: If a user with the provided phone number already exists or if the phone number does not meet the 10-digit requirement, it raises an HTTP exception with a 400 status code and a detailed error message.
    """
    userPresent = user_collection.find_one({"phone": user.phone})  # Check if phone is already registered
    if userPresent:
        raise HTTPException(status_code=400, detail="User already exists!")
    
    # Check if the password is of 10 digits
    if len(str(user.phone)) != 10:
        raise HTTPException(status_code=400, detail="Phone Number should be 10 digits.")

    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password  # Store the hashed password instead of the plain one

    # Convert UserModel instance to a dictionary
    user_dict = dict(user)

    # Remove shopping_cart field if present
    user_dict.pop("shopping_cart", None)

    # Insert the dictionary into MongoDB
    res = user_collection.insert_one(user_dict)

    return JSONResponse(status_code=201, content={"message": "New User Registered.", "user_id": str(res.inserted_id)})



#GET Request Method
@userRouter.get("/user/user-login", tags=["User APIs"])
async def user_login(phone: int, password: str):
    """
    This asynchronous endpoint function handles the user login process. It retrieves user data from the MongoDB database based on the provided phone. If the user is found, it verifies the provided password against the hashed password stored in the database. If the password verification is successful, it returns a welcome message. If the password does not match, it returns an error message indicating the wrong password. If the phone is not found, it returns an error message indicating either the phone or password is incorrect.

Parameters:
- phone (int): The phone of the user attempting to log in. This is used to retrieve the user details from the database.
- password (str): The password provided by the user for login. This password is verified against the hashed password stored in the database.

Returns:
- Dict[str, str]: A dictionary containing either a success message with a welcome note if the login is successful, or an error message if there is an issue with the phone or password.

Raises:
- HTTPException: This function raises an HTTP exception with a 400 status code for the following reasons:
    - If the provided password does not match the stored password.
    - If no user is found with the given phone number.
    """
    userPresent = user_collection.find_one({"phone": phone})
    if userPresent:
        if pwd_context.verify(password, userPresent["password"]):
            return {"message": "Logged In Successfully!, Welcome " + userPresent["first_name"], "user_id": str(userPresent["_id"])}
        else:
            raise HTTPException(status_code=400, detail="Wrong Password!")
    else:
        raise HTTPException(status_code=400, detail="Wrong Phone or Password")



#GET Request Method
@userRouter.get("/user/my-profile", tags=["User APIs"])
async def my_profile(user_id: str):
    """
    This asynchronous endpoint retrieves the profile of a user by their ID. It is associated with the HTTP GET method at the route /user/my-profile. This function is tagged under the "User APIs" category, indicating its purpose for handling user-specific data retrieval.

Parameters:
- user_id (str): The unique identifier for the user, expected to be in string format.

Returns:
- dict: Returns a serialized dictionary of the user's data if found.
- HTTPException: Raises an HTTP 404 exception if no user corresponding to the provided ID is found.

Raises:
- HTTPException: If the user with the specified ID is not registered in the system, an exception is thrown with a status code of 404 and a detail message "User not registered!"
    """
    userPresent = user_collection.find_one({"_id": ObjectId(user_id)})
    if userPresent:
        return individual_serial(userPresent)
    else:
        raise HTTPException(status_code=404, detail="User not registered!")



#PUT Request Method
@userRouter.put("/user/update-user/{user_id}", tags=["User APIs"])
async def update_user(user_id: str,
                      first_name: Optional[str] = None,
                      last_name: Optional[str] = None,
                      username: Optional[str] = None,
                      phone: Optional[int] = None,
                      password: Optional[str] = None,
                      email: Optional[str] = None):
    """
    This asynchronous function facilitates the updating of existing user details via a PUT request at the /user/update-user/{user_id} endpoint. It interacts with a MongoDB collection named user_collection to update fields such as first name, last name, username, phone number, password, and email for a specified user. It performs validations on the phone number and ensures that updated phone numbers are not already registered under a different user.

Parameters:
- user_id (str): The MongoDB _id of the user whose details are to be updated.
- first_name (Optional[str]): The new first name to be set for the user, if provided.
- last_name (Optional[str]): The new last name to be set for the user, if provided.
- username (Optional[str]): The new username to be set for the user, if provided.
- phone (Optional[int]): The new phone number to be set for the user; it must be exactly 10 digits long and not already in use by another user.
- password (Optional[str]): The new password to be set for the user; it will be hashed before storage.
- email (Optional[str]): The new email to be updated for the user, if provided.

Returns:
- dict: A dictionary containing a success message indicating that the user details have been updated.

Raises:
- HTTPException: This function raises an HTTP exception in several cases:
    - If the provided phone number is not exactly 10 digits.
    - If the provided phone number is already registered to a different user.
    - If no user is found with the given user_id.
    """
    
    # Construct the update dictionary with provided fields
    update_dict = {}
    if first_name is not None:
        update_dict["first_name"] = first_name
    if last_name is not None:
        update_dict["last_name"] = last_name
    if username is not None:
        update_dict["username"] = username
    if email is not None:
        update_dict["email"] = email

    # Check if phone number is provided and validate its length
    if phone is not None:
        if len(str(phone)) != 10:
            raise HTTPException(status_code=400, detail="Phone Number should be 10 digits.")
        # Check if the phone number is already used by a different user
        existing_user = user_collection.find_one({"phone": phone, "_id": {"$ne": ObjectId(user_id)}})
        if existing_user:
            raise HTTPException(status_code=400, detail="Phone Number already registered to a different user.")
            
        update_dict["phone"] = phone

    # Hash the password if provided
    if password is not None:
        hashed_password = pwd_context.hash(password)
        update_dict["password"] = hashed_password
    # Update user details in MongoDB
    updated_user = user_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict},
        return_document=ReturnDocument.AFTER
    )

    if updated_user:
        return {"message": "User Details Updated"}
    else:
        raise HTTPException(status_code=404, detail="User not found")



#PUT Request Method
@userRouter.put("/user/update-profile-pic", tags=["User APIs"])
async def update_profile_pic(user_id: str, file: UploadFile = File(...)):
    """
    This asynchronous function allows users to update their profile picture through a PUT request at the /user/update-profile-pic endpoint. It handles the uploading of an image file, saves the file temporarily, uploads it to Cloudinary, and updates the user's profile with the URL of the uploaded image in the MongoDB collection named user_collection.

Parameters:
- user_id (str): The MongoDB _id of the user whose profile picture is to be updated.
- file (UploadFile): The image file uploaded by the user. It uses File(...) as a default value, indicating that the file parameter is required.

Returns:
- dict: A dictionary containing a success message and the secure URL of the updated profile picture.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code if no user is found with the provided user_id.
    """
    
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save the uploaded file locally
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload the file to Cloudinary
    result = cloudinary.uploader.upload(file.filename, folder="Ecommerce-Shopping/Users/" + user_id + "/profile")

    # Remove the local file
    os.remove(file.filename)
        
    user_collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "profile_url": result["secure_url"],
            }}
        )
    return {"message": "URL set successfully!", "profile_url": result['secure_url']}