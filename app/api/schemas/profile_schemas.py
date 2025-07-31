from pydantic import BaseModel, constr, EmailStr
from typing import List


class ProductSummarySchema(BaseModel):

    id: int
    name: constr(min_length=1, max_length=255)
    price: float
    is_sold: bool

    model_config = {
            "from_attributes": True
        }


class UserSubscriptionSchema(BaseModel):

    id: int
    nickname: str
    email: str

    model_config = {
            "from_attributes": True
        }


class UserProfileWithProductsSchema(BaseModel):

    id: int
    nickname: constr(min_length=3, max_length=64)
    email: EmailStr
    wallet: float
    active_products: List[ProductSummarySchema]
    subscriptions: List[UserSubscriptionSchema]

    model_config = {
            "from_attributes": True
        }
