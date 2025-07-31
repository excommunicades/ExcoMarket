from db.models import Subscription, User
from db.extensions import db


def subscribe_to_seller(user_id: int, seller_id: int):
    
    """Subscribe a user to a seller if not already subscribed and valid."""

    if user_id == seller_id:
        return None, "You cannot subscribe to yourself"

    seller = User.query.get(seller_id)
    if not seller:
        return None, "Seller not found"

    existing = Subscription.query.filter_by(subscriber_id=user_id, seller_id=seller_id).first()
    if existing:
        return "Already subscribed", None

    try:
        sub = Subscription(subscriber_id=user_id, seller_id=seller_id)
        db.session.add(sub)
        db.session.commit()
        return "Subscribed successfully", None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def unsubscribe_from_seller(user_id: int, seller_id: int):

    """Unsubscribe a user from a seller if the subscription exists."""

    sub = Subscription.query.filter_by(subscriber_id=user_id, seller_id=seller_id).first()
    if not sub:
        return None, "Subscription not found"

    try:
        db.session.delete(sub)
        db.session.commit()
        return "Unsubscribed successfully", None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
