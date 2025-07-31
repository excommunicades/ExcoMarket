import os
import jwt
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

from flask import request, jsonify

load_dotenv()
secret_key = os.getenv("SECRET_KEY", None)


def create_tokens(user_id: int):

    """Generate access and refresh JWT tokens for a user with user_id."""

    access_token = jwt.encode({
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }, secret_key, algorithm="HS256")

    refresh_token = jwt.encode({
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=7)
    }, secret_key, algorithm="HS256")

    return access_token, refresh_token


def jwt_required(func):

    """Decorator to protect endpoints by validating JWT access token from 'Authorization' header."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = int(payload["sub"])
        except Exception as e:
            return jsonify({"error": "Invalid token", "details": str(e)}), 401
        return func(*args, user_id=user_id, **kwargs)
    return wrapper


def validate_refresh_token(token: str):

    """Validate a refresh JWT token, return associated User or raise error if invalid or expired."""
    
    from db.models import User

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise jwt.InvalidTokenError("Token missing subject")
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Refresh token expired")

    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid refresh token")

    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    return user


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return check_password_hash(hashed, password)
