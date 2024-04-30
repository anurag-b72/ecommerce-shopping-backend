from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class cartModel(BaseModel):
    product_id: Optional[str] = None
    quantity: Optional[int] = None

class OrderModel(BaseModel):    
    user_id: str
    user_address: str
    user_phone: int
    shopping_cart: List[cartModel]
    total_price: float
    purchase_time: datetime
    order_approval_status: str = "Pending"