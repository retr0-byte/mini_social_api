from typing import Protocol, TypeVar, Generic, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped


class HasId(Protocol):
    id: Mapped[int]

T = TypeVar("T", bound=HasId)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, item_id: int) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()