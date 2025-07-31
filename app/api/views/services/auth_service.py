from jwt import ExpiredSignatureError, InvalidTokenError

from db.models import User
from db.extensions import db

from api.views.utils import (
    hash_password,
    verify_password,
    create_tokens,
    validate_refresh_token
)


def register_user(data):

    """Register a new user if email and nickname are unique."""

    if User.query.filter((User.email == data.email) | (User.nickname == data.nickname)).first():
        return None, "Email or nickname already exists"

    user = User(
        nickname=data.nickname,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    try:
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def login_user(data):

    """Authenticate user and generate access and refresh tokens."""

    user = User.query.filter(
        (User.email == data.nickname_or_email) | (User.nickname == data.nickname_or_email)
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        return None, "Invalid credentials"

    access_token, refresh_token = create_tokens(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }, None


def refresh_user_token(refresh_token):

    """Validate a refresh token and return a new access token."""

    try:
        user = validate_refresh_token(refresh_token)
        access_token, _ = create_tokens(user.id)
        return access_token, None
    except ExpiredSignatureError:
        return None, "Refresh token expired"
    except InvalidTokenError:
        return None, "Invalid refresh token"
    except ValueError as e:
        return None, str(e)
