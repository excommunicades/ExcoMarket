from pydantic import BaseModel, constr, PositiveFloat, field_validator
from typing import Optional, List


class SellerInfoSchema(BaseModel):

    id: int
    nickname: constr(min_length=3, max_length=64)

    model_config = {
        "from_attributes": True
    }


class ProductCreateSchema(BaseModel):

    name: constr(min_length=1, max_length=128)
    price: float
    description: Optional[str] = None

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ProductDetailSchema(BaseModel):

    id: int
    name: constr(min_length=1, max_length=255)
    price: PositiveFloat
    description: str
    is_sold: bool
    seller: SellerInfoSchema

    model_config = {
        "from_attributes": True
    }


class ProductSummarySchema(BaseModel):

    id: int
    name: constr(min_length=1, max_length=255)
    price: PositiveFloat

    model_config = {
        "from_attributes": True
    }


class ProductsListSchema(BaseModel):

    products: List[ProductSummarySchema]

    model_config = {
        "from_attributes": True
    }


class ProductUpdateSchema(BaseModel):

    name: Optional[constr(min_length=1, max_length=128)]
    price: Optional[float]
    description: Optional[str]

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ProductResponseSchema(BaseModel):

    id: int
    name: str
    price: float
    description: Optional[str]
    seller_id: int
    is_sold: bool

    model_config = {
        "from_attributes": True
    }
