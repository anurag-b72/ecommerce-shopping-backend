from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import cloudinary
import cloudinary.uploader
import os
from pymongo import ReturnDocument
from typing import Optional


from models.ProductModel import ProductModel
from config.db import product_collection
from schemas.product_schema import *
from bson import ObjectId

productRouter = APIRouter()  

# POST Request Method
@productRouter.post("/product/add-product", tags=["Product APIs"])
async def add_product(name: str, description: str, price: float, image: UploadFile = File(None)):
    """
    This asynchronous function handles the addition of new products via a POST request at the /product/add-product endpoint. It involves adding product details to a MongoDB collection (product_collection) and optionally uploading an image file to Cloudinary if provided. The function first saves the image locally, uploads it to Cloudinary, and then removes the local file. The MongoDB document for the product includes the name, description, price, and the URL of the uploaded image.

Parameters:
- name (str): The name of the product.
- description (str): A detailed description of the product.
- price (float): The price of the product.
- image (UploadFile, optional): An optional image file of the product, which will be uploaded to Cloudinary if provided.

Returns:
- JSONResponse: A JSON response that includes a success message, the MongoDB inserted_id of the new product, and optionally the URL of the uploaded product image.
    """
    
    # If image is provided, save and upload it to Cloudinary
    if image:
        # Save the uploaded file locally
        with open(image.filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Upload the file to Cloudinary
        result = cloudinary.uploader.upload(image.filename, folder="Ecommerce-Shopping/Products")
        
        # Remove the local file
        os.remove(image.filename)

        # Insert image document in MongoDB
        product_doc = product_collection.insert_one(
            {
                "name": name,
                "description": description,
                "price": price,  
                "image_url": result['secure_url'],
            }
        )
        return JSONResponse(status_code=201, content={"message": "New Product Added Successfully.", "product_id": str(product_doc.inserted_id), "product_image_url": result['secure_url']})


    default_product_url = "https://res.cloudinary.com/db0nvjc2z/image/upload/v1714307476/Ecommerce-Shopping/Products/shopping-cart_tlud4v.png"
    # Insert image document in MongoDB
    product_doc = product_collection.insert_one(
        {
            "name": name,
            "description": description,
            "price": price,  
            "image_url": default_product_url,
        }
    )
    return JSONResponse(status_code=201, content={"message": "New Product Added Successfully.", "product_id": str(product_doc.inserted_id), "product_image_url": default_product_url})



@productRouter.put("/product/edit-product/{product_id}", tags=["Product APIs"])
async def edit_product(product_id: str, name: str = None, description: str = None, price: float = None, image: UploadFile = File(None)):
    """
    This asynchronous function handles the editing of product details via a PUT request at the /product/edit-product/{product_id} endpoint. It checks for the existence of a product in the product_collection of a MongoDB database and updates its fields, such as name, description, price, and optionally the product image. If a new image is provided, the function uploads it to Cloudinary, updates the product's image URL, and cleans up the local file storage.

Parameters:
- product_id (str): The MongoDB _id of the product to be edited.
- name (Optional[str]): The new name of the product, if provided.
- description (Optional[str]): The new description of the product, if provided.
- price (Optional[float]): The new price of the product, if provided.
- image (UploadFile, optional): An optional new image file for the product. If provided, the image is uploaded to Cloudinary and its URL is updated in the database.

Returns:
- dict: A dictionary containing a message indicating successful update of the product and the product's MongoDB _id.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code if no product is found with the specified product_id. It also raises an HTTP exception with a 500 status code if any other errors occur during the update process.

    """
    try:
        # Check if the product exists
        existing_product = product_collection.find_one({"_id": ObjectId(product_id)})
        if existing_product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        # If image is provided, save and upload it to Cloudinary
        if image:
            # Save the uploaded file locally
            with open(image.filename, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            # Upload the file to Cloudinary
            result = cloudinary.uploader.upload(image.filename, folder="Ecommerce-Shopping/Products")
            
            # Remove the local file
            os.remove(image.filename)

            # Update the product's image_url field with the Cloudinary URL
            product_collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": {"image_url": result['secure_url']}}
            )

        # Update the product details in MongoDB
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if price is not None:
            update_data["price"] = price
        
        if update_data:
            product_collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )

        return {"message": "Product Updated Successfully", "product_id": product_id}

    except Exception as e:
        # If any exception occurs during the process, handle it
        raise HTTPException(status_code=500, detail="An error occurred while editing the product")



@productRouter.delete("/product/delete-product/{product_id}", tags=["Product APIs"])
async def delete_product(product_id: str):
    """
    This asynchronous function facilitates the deletion of a product via a DELETE request at the /product/delete-product/{product_id} endpoint. It interacts with a MongoDB collection named product_collection to remove a product specified by its MongoDB _id. The function first verifies whether the product exists in the database. If it exists, it proceeds to delete it; otherwise, it raises an HTTP exception.

Parameters:
- product_id (str): The MongoDB _id of the product to be deleted.

Returns:
- dict: A dictionary containing a message indicating successful deletion of the product and the product's MongoDB _id.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code if no product is found with the specified product_id.

    """
    # Check if the product exists
    existing_product = product_collection.find_one({"_id": ObjectId(product_id)})
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete the product from MongoDB
    product_collection.delete_one({"_id": ObjectId(product_id)})
    
    return {"message": "Product Deleted Successfully", "product_id": product_id}



@productRouter.get("/product/get-product/{product_id}", tags=["Product APIs"])
async def get_product(product_id: str):
    """
    This asynchronous function handles retrieving a specific product by its MongoDB _id via a GET request at the /product/get-product/{product_id} endpoint. It searches for the product in the product_collection of a MongoDB database. If the product is found, it serializes the MongoDB document using a function individual_serial, which should be designed to convert the MongoDB document into a more readable and structured JSON format suitable for API responses.

Parameters:
- product_id (str): The MongoDB _id of the product to be retrieved.

Returns:
- The serialized product data: This depends on the implementation of the individual_serial function but typically includes detailed information about the product in a JSON format.

Raises:
- HTTPException: This function raises an HTTP exception with a 404 status code if no product is found with the specified product_id.

    """
    # Find the product in MongoDB
    product = product_collection.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return individual_serial(product)



@productRouter.get("/product/get-all-products", tags=["Product APIs"])
async def get_all_products():
    """
    This asynchronous function retrieves all products from a MongoDB collection via a GET request at the /product/get-all-products endpoint. It fetches all entries from the product_collection and serializes them using a function list_serial, which is designed to convert the MongoDB documents into a JSON-compatible list format suitable for API responses.

Returns:
- list: A list of all serialized products. The structure of the returned list depends on the implementation of the list_serial function, but typically includes detailed information about each product formatted for JSON output.

    """
    # Fetch all products from MongoDB
    products = product_collection.find()
    return list_serial(products)