import random
from sqlalchemy import text
from datetime import datetime

from db.extensions import db
from db.models import Product, User

SECTORS = {
    'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Tablet'],
    'Books': ['Novel', 'Biography', 'Textbook', 'Comic', 'Magazine'],
    'Clothing': ['T-shirt', 'Jeans', 'Jacket', 'Dress', 'Sweater'],
    'Home Appliances': ['Microwave', 'Vacuum', 'Blender', 'Toaster', 'Fridge'],
    'Toys': ['Puzzle', 'Doll', 'RC Car', 'Lego Set', 'Board Game'],
    'Sports': ['Football', 'Basketball', 'Tennis Racket', 'Running Shoes', 'Yoga Mat'],
    'Office': ['Notebook', 'Pen', 'Desk Chair', 'Monitor Stand', 'Stapler'],
    'Beauty': ['Lipstick', 'Shampoo', 'Perfume', 'Face Cream', 'Hair Dryer'],
    'Food': ['Chocolate', 'Coffee', 'Olive Oil', 'Cheese', 'Honey'],
    'Garden': ['Hose', 'Shovel', 'Gloves', 'Plant Pot', 'Fertilizer']
}


def check_database_connection():

    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connected successfully"}, None
    except Exception as e:
        return None, str(e)


def create_random_products(user_id: int):

    """Generate and insert 50 random products for the given user."""

    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    products_to_create = []

    for sector, product_names in SECTORS.items():
        for i in range(5):
            name = f"{product_names[i]} {random.randint(1000, 9999)}"
            price = round(random.uniform(10, 1000), 2)
            description = f"High quality {product_names[i].lower()} from {sector.lower()} sector."

            products_to_create.append(Product(
                name=name,
                price=price,
                description=description,
                seller_id=user.id,
                is_sold=False,
                created_at=datetime.utcnow()
            ))

    try:
        db.session.bulk_save_objects(products_to_create)
        db.session.commit()
        return len(products_to_create), None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def get_all_users_service():

    try:
        users = User.query.all()
        users_list = [
            {
                "id": user.id,
                "nickname": user.nickname,
            }
            for user in users
        ]
        return users_list, None
    except Exception as e:
        return None, str(e)
