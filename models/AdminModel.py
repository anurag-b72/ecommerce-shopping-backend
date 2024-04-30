from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Admin(BaseModel):
    admin_first_name: str
    admin_last_name: str
    admin_username: str
    admin_password: str
    # admin_role: str
    created_at: Optional[datetime]
    email: Optional[str]