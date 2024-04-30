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
    # Check if the product exists
    existing_product = product_collection.find_one({"_id": ObjectId(product_id)})
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete the product from MongoDB
    product_collection.delete_one({"_id": ObjectId(product_id)})
    
    return {"message": "Product Deleted Successfully", "product_id": product_id}



@productRouter.get("/product/get-product/{product_id}", tags=["Product APIs"])
async def get_product(product_id: str):
    # Find the product in MongoDB
    product = product_collection.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return individual_serial(product)



@productRouter.get("/product/get-all-products", tags=["Product APIs"])
async def get_all_products():
    # Fetch all products from MongoDB
    products = product_collection.find()
    return list_serial(products)