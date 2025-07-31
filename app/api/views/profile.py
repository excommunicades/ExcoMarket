from flasgger import swag_from

from flask import Blueprint, jsonify

from api.views.utils import jwt_required
from api.views.services.profile_service import get_user_profile_with_products

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET"])
@swag_from("swagger/profile/get_profile.yaml")
@jwt_required
def get_profile(user_id):

    """Retrieve authenticated user's profile along with their products; no input required."""

    profile_data, error = get_user_profile_with_products(user_id)

    if error == "User not found":
        return jsonify({"error": error}), 404
    elif error:
        return jsonify({"error": "Unknown error", "details": error}), 500

    return jsonify(profile_data.dict()), 200
