from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, PositiveInt, constr


class Customer(BaseModel):
    customer_id: constr(min_length=1)
    customer_name: constr(min_length=1)
    email: Optional[EmailStr]
    phone: Optional[str]
    state: Optional[constr(min_length=2, max_length=2)]
    created_at: Optional[datetime]


class Product(BaseModel):
    product_id: constr(min_length=1)
    product_name: constr(min_length=1)
    category: Optional[str]
    price: float = Field(gt=0)
    created_at: Optional[datetime]


class Sale(BaseModel):
    sale_id: constr(min_length=1)
    sale_date: date
    customer_id: constr(min_length=1)
    product_id: constr(min_length=1)
    quantity: PositiveInt
    unit_price: float = Field(gt=0)
    total_value: float = Field(gt=0)
    year: int
    month: int
    quarter: int
    state: Optional[constr(min_length=2, max_length=2)]
    category: Optional[str]
