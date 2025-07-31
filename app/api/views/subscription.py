from flasgger import swag_from
from flask import Blueprint, jsonify

from api.views.utils import jwt_required
from api.views.services.subscription_service import subscribe_to_seller, unsubscribe_from_seller


subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscriptions")


@subscription_bp.route("/subscribe/<int:seller_id>", methods=["POST"])
@swag_from("swagger/subscription/subscribe.yaml")
@jwt_required
def subscribe(user_id, seller_id):

    """Subscribe the authenticated user to a seller; seller_id in URL path."""

    message, error = subscribe_to_seller(user_id, seller_id)

    if error == "You cannot subscribe to yourself":
        return jsonify({"error": error}), 400
    if error == "Seller not found":
        return jsonify({"error": error}), 404
    if error:
        return jsonify({"error": "Failed to subscribe", "details": error}), 500

    if message == "Already subscribed":
        return jsonify({"message": message}), 200

    return jsonify({"message": message}), 201


@subscription_bp.route("/unsubscribe/<int:seller_id>", methods=["POST"])
@swag_from("swagger/subscription/unsubscribe.yaml")
@jwt_required
def unsubscribe(user_id, seller_id):

    """Unsubscribe the authenticated user from a seller; seller_id in URL path."""

    message, error = unsubscribe_from_seller(user_id, seller_id)

    if error == "Subscription not found":
        return jsonify({"error": error}), 404
    if error:
        return jsonify({"error": "Failed to unsubscribe", "details": error}), 500

    return jsonify({"message": message}), 200
