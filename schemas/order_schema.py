def individual_serial(order)-> dict:
    return{
        "id": str(order.get("_id")),
        "user_id": order.get("user_id"),
        "user_address": order.get("user_address"),
        "user_phone": order.get("user_phone"),
        "shopping_cart": order.get("shopping_cart"),
        "total_price": order.get("total_price"),
        "purchase_time": order.get("purchase_time"),
    }

def list_serial(orders) -> list:
    return [individual_serial(order) for order in orders]