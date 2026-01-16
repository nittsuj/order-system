from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

# PRODUCT SCHEMAS
class ProductBase(BaseModel):
    name: str = Field(max_length=255)
    price: int
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# ORDER SCHEMAS
class OrderBase(BaseModel):
    status: str

class OrderCreate(OrderBase):
    users_id: int

class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    products: List[ProductResponse] = []

# USER SCHEMAS
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=3, max_length=254)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    orders: List[OrderResponse] = []
