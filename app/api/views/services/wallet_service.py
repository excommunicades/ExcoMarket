from db.models import User
from db.extensions import db


def reward_user_balance(user_id: int, amount: int = 500):

    """Add a specified amount to a user's wallet balance."""

    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    try:
        user.wallet += amount
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def clear_user_balance(user_id: int):

    """Reset a user's wallet balance to zero."""

    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    try:
        user.wallet = 0
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
