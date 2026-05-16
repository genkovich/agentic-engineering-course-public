"""Catalog HTTP handler — GET /products."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.catalog.app.service import Service


class ProductDTO(BaseModel):
    id: str
    name: str
    price_cents: int
    category_id: str


class ProductsResp(BaseModel):
    products: list[ProductDTO]


def build_router(svc: Service) -> APIRouter:
    router = APIRouter(tags=["catalog"])

    @router.get("/products", response_model=ProductsResp)
    async def list_products() -> ProductsResp:
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

    return router
