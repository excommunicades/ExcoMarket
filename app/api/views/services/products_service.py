from db.extensions import db
from db.models import Product, User
from events.producers.products_producer import send_new_product_event


def create_product_service(user_id, data):

    """Create a new product for the specified seller."""

    seller = User.query.get(user_id)
    if not seller:
        return None, "Seller not found"

    product = Product(
        name=data.name,
        price=data.price,
        description=data.description,
        seller_id=seller.id
    )
    try:
        db.session.add(product)
        db.session.commit()
        send_new_product_event(product)
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def get_all_available_products():

    """Retrieve all unsold products, is_sold=False."""

    return Product.query.filter_by(is_sold=False).all()


def get_product_by_id(product_id):

    return Product.query.get(product_id)


def update_product_service(product_id, user_id, data):

    """Update a product's details if user is the seller."""

    product = Product.query.get(product_id)
    if not product:
        return None, "Product not found"

    if product.seller_id != user_id:
        return None, "Forbidden"

    product.name = data.name
    if data.price is not None:
        product.price = data.price
    if data.description is not None:
        product.description = data.description

    try:
        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_product_service(product_id, user_id):

    """Delete a product if user is the seller."""

    product = Product.query.get(product_id)
    if not product:
        return "Product not found", 404

    if product.seller_id != user_id:
        return "Forbidden", 403

    try:
        db.session.delete(product)
        db.session.commit()
        return None, 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500


def purchase_product_service(product_id, user_id):

    """Handle product purchase transaction between buyer and seller."""

    buyer = User.query.get(user_id)
    if not buyer:
        return "Buyer not found", 404

    product = Product.query.get(product_id)
    if not product or product.is_sold:
        return "Product not available", 404

    if product.seller_id == user_id:
        return "Cannot buy your own product", 400

    if buyer.wallet < product.price:
        return "Insufficient funds", 400

    seller = User.query.get(product.seller_id)
    if not seller:
        return "Seller not found", 404

    try:
        buyer.wallet -= product.price
        seller.wallet += product.price
        product.is_sold = True
        db.session.commit()
        return None, 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500
