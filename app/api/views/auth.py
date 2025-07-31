from flask import Blueprint, request, jsonify
from flasgger import swag_from
from pydantic import ValidationError

from api.schemas.auth_schemas import (
    LoginSchema,
    RegisterSchema,
    UserResponse,
)
from api.views.services.auth_service import (
    register_user,
    login_user,
    refresh_user_token,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
@swag_from("swagger/auth/register.yaml")
def register():

    """Register a new user; send JSON with 'nickname', 'email', and 'password'."""

    try:
        data = RegisterSchema(**request.json)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    user, error = register_user(data)
    if error == "Email or nickname already exists":
        return jsonify({"error": error}), 409
    elif error:
        return jsonify({"error": "Registration failed", "details": error}), 500

    return jsonify({"message": "Registration successful"}), 201


@auth_bp.route("/login", methods=["POST"])
@swag_from("swagger/auth/login.yaml")
def login():

    """Authenticate user; send JSON with 'nickname_or_email' and 'password'."""

    try:
        data = LoginSchema(**request.json)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    result, error = login_user(data)
    if error == "Invalid credentials":
        return jsonify({"error": error}), 401
    elif error:
        return jsonify({"error": "Login failed", "details": error}), 500

    return jsonify({
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "user": UserResponse.from_orm(result["user"]).dict()
    }), 200


@auth_bp.route("/token/refresh", methods=["POST"])
@swag_from("swagger/auth/refresh_token.yaml")
def refresh_token_view():

    """Refresh access token; send JSON with 'refresh_token'."""

    data = request.json
    if not data or "refresh_token" not in data:
        return jsonify({"error": "refresh_token is required"}), 400

    access_token, error = refresh_user_token(data["refresh_token"])
    if error == "Refresh token expired":
        return jsonify({"error": error}), 401
    elif error == "Invalid refresh token":
        return jsonify({"error": error}), 401
    elif error:
        return jsonify({"error": error}), 404

    return jsonify({"access_token": access_token}), 200
