from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Sequence, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import Item


class ItemRepository(ABC):
    @abstractmethod
    async def create(self, *, name: str, description: str) -> Item: ...
    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[Item]: ...
    @abstractmethod
    async def list(
        self, *, limit: int = 50, offset: int = 0, q: str | None = None
    ) -> Sequence[Item]: ...
    @abstractmethod
    async def update(
        self,
        item_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Item]: ...
    @abstractmethod
    async def delete(self, item_id: str) -> bool: ...


class SqlAlchemyItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, name: str, description: str) -> Item:
        item = Item(name=name, description=description)
        self.session.add(item)
        await self.session.flush()  # assigns PK
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: str) -> Optional[Item]:
        res = await self.session.execute(select(Item).where(Item.id == item_id))
        return res.scalar_one_or_none()

    async def list(self, *, limit: int = 50, offset: int = 0, q: str | None = None):
        stmt = select(Item)
        if q:
            like = f"%{q}%"
            stmt = stmt.where((Item.name.ilike(like)) | (Item.description.ilike(like)))
        stmt = (
            stmt.order_by(Item.created_at.desc())
            .limit(min(max(limit, 1), 200))
            .offset(max(offset, 0))
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def update(
        self,
        item_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Item]:
        fields = {}
        if name is not None:
            fields["name"] = name
        if description is not None:
            fields["description"] = description
        if not fields:
            return await self.get_by_id(item_id)

        stmt = update(Item).where(Item.id == item_id).values(**fields).returning(Item)
        res = await self.session.execute(stmt)
        row = res.fetchone()
        return row[0] if row else None

    async def delete(self, item_id: str) -> bool:
        res = await self.session.execute(delete(Item).where(Item.id == item_id))
        return res.rowcount == 1
