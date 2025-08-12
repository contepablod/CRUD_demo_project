from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Optional
from app.schemas.item import ItemCreate, ItemUpdate, ItemOut
from app.services.items import ItemService
from app.persistence.repositories import SqlAlchemyItemRepository
from app.db.connection import session_scope
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/items", tags=["items"])


async def get_service() -> ItemService:
    async with session_scope() as session:  # one-unit-of-work per request
        # yield a service bound to this session
        yield ItemService(SqlAlchemyItemRepository(session))


@router.get("/", response_model=list[ItemOut])
async def list_items(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None),
    svc: Annotated[ItemService, Depends(get_service)] = None,
):
    return await svc.list(limit=limit, offset=offset, q=q)


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: str, svc: Annotated[ItemService, Depends(get_service)] = None
):
    item = await svc.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.post("/", response_model=ItemOut, status_code=201)
async def create_item(
    payload: ItemCreate, svc: Annotated[ItemService, Depends(get_service)] = None
):
    return await svc.create(**payload.model_dump())


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: str,
    payload: ItemUpdate,
    svc: Annotated[ItemService, Depends(get_service)] = None,
):
    if not any(v is not None for v in payload.model_dump().values()):
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = await svc.update(item_id, **payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: str, svc: Annotated[ItemService, Depends(get_service)] = None
):
    ok = await svc.delete(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
