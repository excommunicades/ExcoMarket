from db.models import User, Product, Subscription
from api.schemas.profile_schemas import UserProfileWithProductsSchema


def get_user_profile_with_products(user_id: int):

    user = User.query.get(user_id)
    if not user:
        return None, "User not found"

    products = Product.query.filter_by(seller_id=user.id).all()

    subscriptions = (
        User.query
        .join(Subscription, Subscription.seller_id == User.id)
        .filter(Subscription.subscriber_id == user.id)
        .all()
    )

    profile_data = UserProfileWithProductsSchema(
        id=user.id,
        nickname=user.nickname,
        email=user.email,
        wallet=user.wallet,
        active_products=products,
        subscriptions=subscriptions,
    )

    return profile_data, None
