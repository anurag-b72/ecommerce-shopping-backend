from pydantic import BaseModel
from typing import Optional

class ProductModel(BaseModel):
    name: str
    description: str
    price: float
    image_url: Optional[str] = "https://res.cloudinary.com/db0nvjc2z/image/upload/v1714307476/Ecommerce-Shopping/Products/shopping-cart_tlud4v.png"