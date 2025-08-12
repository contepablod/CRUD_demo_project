from collections.abc import Sequence

from app.domain.models import Item
from app.persistence.repositories import ItemRepository


class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    async def create(self, *, name: str, description: str) -> Item:
        # Place to enforce rules/quotas/uniqueness checks
        return await self.repo.create(name=name, description=description)

    async def get(self, item_id: str) -> Item | None:
        return await self.repo.get_by_id(item_id)

    async def list(
        self, *, limit: int = 50, offset: int = 0, q: str | None = None
    ) -> Sequence[Item]:
        return await self.repo.list(limit=limit, offset=offset, q=q)

    async def update(
        self, item_id: str, *, name: str | None = None, description: str | None = None
    ) -> Item | None:
        return await self.repo.update(item_id, name=name, description=description)

    async def delete(self, item_id: str) -> bool:
        return await self.repo.delete(item_id)
