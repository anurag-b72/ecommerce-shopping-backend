def individual_serial(user)-> dict:
    return{
        "id": str(user.get("_id")),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "username": user.get("username"),
        "phone": user.get("phone"),
        # "password": user.get("password"), # As we don't intend to show password
        "email": user.get("email"),
        "profile_url": user.get("profile_url"),
        "shopping_cart": user.get("shopping_cart"),
    }

def list_serial(users) -> list:
    return [individual_serial(user) for user in users]