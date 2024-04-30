from pydantic import BaseModel
from typing import Optional, List

class cartModel(BaseModel):
    product_id: Optional[str] = None
    quantity: Optional[int] = None

class UserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: int
    password: str
    email: Optional[str] = None
    profile_url: Optional[str] = 'https://rb.gy/w1bm3w'
    shopping_cart: Optional[List[cartModel]] = None