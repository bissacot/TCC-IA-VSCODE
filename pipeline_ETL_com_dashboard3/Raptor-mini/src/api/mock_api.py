from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


@app.get("/products")
async def get_products() -> list[Product]:
    return [
        {"product_id": 1, "name": "Widget A", "category": "Widgets", "price": 25.0},
        {"product_id": 2, "name": "Widget B", "category": "Widgets", "price": 33.5},
        {"product_id": 3, "name": "Gadget C", "category": "Gadgets", "price": 18.75},
    ]
