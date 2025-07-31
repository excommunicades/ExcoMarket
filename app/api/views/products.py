from flasgger import swag_from
from pydantic import ValidationError

from flask import Blueprint, request, jsonify

from api.schemas.products_schemas import (
    ProductsListSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductDetailSchema, 
    ProductSummarySchema,
    ProductResponseSchema,
)
from api.views.services.products_service import (
    get_product_by_id,
    delete_product_service,
    create_product_service,
    update_product_service,
    purchase_product_service,
    get_all_available_products,
)
from api.views.utils import jwt_required
from events.producers.products_producer import send_new_product_event

product_bp = Blueprint("product", __name__, url_prefix="/products")


@product_bp.route("", methods=["POST"])
@swag_from("swagger/products/create_product.yaml")
@jwt_required
def create_product(user_id):

    """Create a new product; send JSON with 'name', 'price', and 'description'."""

    try:
        data = ProductCreateSchema(**request.json)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    product, error = create_product_service(user_id, data)
    if error == "Seller not found":
        return jsonify({"error": error}), 404
    elif error:
        return jsonify({"error": "Failed to create product", "details": error}), 500

    return jsonify(ProductResponseSchema.from_orm(product).dict()), 201


@product_bp.route("", methods=["GET"])
@swag_from("swagger/products/get_all_products.yaml")
def get_all_products():

    """Get a list of all available (unsold) products; no input required."""

    products = get_all_available_products()
    products_data = [ProductSummarySchema.from_orm(p) for p in products]
    return jsonify(ProductsListSchema(products=products_data).dict()), 200


@product_bp.route("/<int:product_id>", methods=["GET"])
@swag_from("swagger/products/get_product_detail.yaml")
def get_product_detail(product_id):

    """Get detailed info of a product by ID; product_id in URL path."""

    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(ProductDetailSchema.from_orm(product).dict()), 200


@product_bp.route("/<int:product_id>", methods=["PATCH"])
@swag_from("swagger/products/update_product.yaml")
@jwt_required
def update_product(product_id, user_id):

    """Update product fields (name, price, description); send JSON with fields to update."""

    try:
        data = ProductUpdateSchema(**request.json)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    product, error = update_product_service(product_id, user_id, data)
    if error == "Product not found":
        return jsonify({"error": error}), 404
    elif error == "Forbidden":
        return jsonify({"error": "You are not the seller of this product"}), 403
    elif error:
        return jsonify({"error": "Failed to update product", "details": error}), 500

    return jsonify(ProductResponseSchema.from_orm(product).dict()), 200



@product_bp.route("/<int:product_id>", methods=["DELETE"])
@swag_from("swagger/products/delete_product.yaml")
@jwt_required
def delete_product(product_id, user_id):

    """Delete a product by ID; product_id in URL path."""

    error, status = delete_product_service(product_id, user_id)
    if status == 404:
        return jsonify({"error": error}), 404
    elif status == 403:
        return jsonify({"error": error}), 403
    elif status == 500:
        return jsonify({"error": "Failed to delete product", "details": error}), 500

    return jsonify({"message": "Product deleted successfully"}), 200


@product_bp.route("/purchase/<int:product_id>", methods=["POST"])
@swag_from("swagger/products/purchase_product.yaml")
@jwt_required
def purchase_product_view(product_id, user_id):

    """Purchase a product by ID; product_id in URL path."""

    error, status = purchase_product_service(product_id, user_id)

    if status == 404:
        return jsonify({"error": error}), 404
    elif status == 400:
        return jsonify({"error": error}), 400
    elif status == 500:
        return jsonify({"error": "Transaction failed", "details": error}), 500

    return jsonify({"message": "Purchase successful"}), 200
