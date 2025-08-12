from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import session_scope
from app.persistence.repositories import SqlAlchemyItemRepository
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.services.items import ItemService

router = APIRouter(prefix="/items", tags=["items"])


# yield the session (unit-of-work per request)
async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_scope() as session:
        yield session


# build the service from the session
async def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> ItemService:
    return ItemService(SqlAlchemyItemRepository(session))


@router.get("/", response_model=list[ItemOut])
async def list_items(
    svc: Annotated[ItemService, Depends(get_service)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None),
):
    return await svc.list(limit=limit, offset=offset, q=q)


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: str,
    svc: Annotated[ItemService, Depends(get_service)],
):
    item = await svc.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.post("/", response_model=ItemOut, status_code=201)
async def create_item(
    payload: ItemCreate,
    svc: Annotated[ItemService, Depends(get_service)],
):
    return await svc.create(**payload.model_dump())


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: str,
    payload: ItemUpdate,
    svc: Annotated[ItemService, Depends(get_service)],
):
    if not any(v is not None for v in payload.model_dump().values()):
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = await svc.update(item_id, **payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    svc: Annotated[ItemService, Depends(get_service)],
):
    ok = await svc.delete(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
