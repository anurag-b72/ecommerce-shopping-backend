def individual_serial(product)-> dict:
    return{
        "id": str(product.get("_id")),
        "name": product.get("name"),
        "description": product.get("description"),
        "price": product.get("price"),
        "image_url": product.get("image_url"),
    }

def list_serial(products) -> list:
    return [individual_serial(product) for product in products]