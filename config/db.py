from pymongo import MongoClient 
import cloudinary

client = MongoClient("mongodb+srv://anuragbiswal2002:24KtXHv0yOVJQ8Oy@cluster0.eyyvpjq.mongodb.net/")

# Databases
admin_db = client.Ecommerce_Admin
user_db = client.User
product_db = client.Product
order_db = client.Order

# Collections
user_collection = user_db["user_collection"]
admin_collection = admin_db["admin_collection"]
product_collection = product_db["product_collection"]
order_collection = order_db["order_collection"]


# Cloudinary API Configuration
cloudinary.config(
    cloud_name="db0nvjc2z",
    api_key="794774291977841",
    api_secret="deiAjkPPn5Au78B6S-RuTjFNXAk"
)