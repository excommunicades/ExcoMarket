import random
from sqlalchemy import text
from datetime import datetime
from flasgger import swag_from

from flask import Blueprint, jsonify

from api.views.utils import jwt_required
from api.views.services.manage_service import check_database_connection, create_random_products, get_all_users_service


manage_bp = Blueprint("manage", __name__, url_prefix="/manage")


@manage_bp.route("/health", methods=["GET"])
@swag_from("swagger/manage/health_check.yaml")
def health_check():

    """Check database connection health; no input required."""

    result, error = check_database_connection()
    if error:
        return jsonify({"status": "error", "message": error}), 500
    return jsonify(result), 200


@manage_bp.route("/populate/products", methods=["POST"])
@swag_from("swagger/manage/create_bulk_products.yaml")
@jwt_required
def create_bulk_products(user_id):

    """Create 50 random products for the authenticated user; no request body required."""

    count, error = create_random_products(user_id)
    if error == "User not found":
        return jsonify({'msg': error}), 404
    elif error:
        return jsonify({'msg': 'Failed to create products', 'details': error}), 500

    return jsonify({'msg': f'{count} products created successfully.'}), 201


@manage_bp.route("/users", methods=["GET"])
@swag_from("swagger/manage/get_all_users.yaml")
def get_all_users():
    users_list, error = get_all_users_service()
    if error:
        return jsonify({"error": "Failed to fetch users", "details": error}), 500
    return jsonify({"users": users_list}), 200
