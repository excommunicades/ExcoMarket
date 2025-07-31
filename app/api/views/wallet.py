from flasgger import swag_from
from flask import Blueprint, jsonify

from api.views.utils import jwt_required
from api.views.services.wallet_service import reward_user_balance, clear_user_balance


wallet_bp = Blueprint("wallet", __name__, url_prefix="/wallet")


@wallet_bp.route("/reward", methods=["POST"])
@swag_from("swagger/wallet/reward_user.yaml")
@jwt_required
def reward_user(user_id):

    """Rewards the authenticated user with 500 coins; no input required."""

    user, error = reward_user_balance(user_id)
    if error == "User not found":
        return jsonify({"error": error}), 404
    elif error:
        return jsonify({"error": "Failed to reward user", "details": error}), 500

    return jsonify({
        "message": "You have been rewarded with 500 coins!",
        "new_balance": user.wallet
    }), 200


@wallet_bp.route("/clear", methods=["POST"])
@swag_from("swagger/wallet/clear_money.yaml")
@jwt_required
def clear_money(user_id):

    """Resets the authenticated user's wallet balance to zero; no input required."""

    user, error = clear_user_balance(user_id)
    if error == "User not found":
        return jsonify({"error": error}), 404
    elif error:
        return jsonify({"error": "Failed to clear money", "details": error}), 500

    return jsonify({
        "message": "Your money has been reset to zero.",
        "new_balance": user.wallet
    }), 200
