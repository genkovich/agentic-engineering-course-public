from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.catalog.repository import Repository
from app.features.catalog.service import Service
from app.shared.db import get_session

router = APIRouter(tags=["catalog"])


class ProductDTO(BaseModel):
    id: str
    name: str
    price_cents: int
    category_id: str


class ProductsResp(BaseModel):
    products: list[ProductDTO]


@router.get("/products", response_model=ProductsResp)
async def list_products(
    session: AsyncSession = Depends(get_session),
) -> ProductsResp:
    svc = Service(Repository(session))
    products = await svc.list()
    return ProductsResp(
        products=[
            ProductDTO(
                id=str(p.id),
                name=p.name,
                price_cents=p.price_cents,
                category_id=str(p.category_id),
            )
            for p in products
        ]
    )
