from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PostLikes
from app.repositories.base_repo import BaseRepository


class LikeRepository(BaseRepository):
    def __init__(self, session: AsyncSession,):
        super().__init__(session, PostLikes)

    async def post_like(
            self,
            post_id: int,
            user_id: int
    ):
        try:
            new_post_like = PostLikes(post_id=post_id, user_id=user_id)
            self.session.add(new_post_like)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()

    async def post_unlike(
            self,
            post_id: int,
            user_id: int
    ):
        await self.session.execute(
            delete(PostLikes).where(
                PostLikes.post_id == post_id,
                PostLikes.user_id == user_id,
            )
        )

        await self.session.commit()

    async def get_likes_count(
            self,
            post_id: int
    ) -> int:
        stmt = select(func.count()).select_from(PostLikes).where(PostLikes.post_id == post_id)
        result = await self.session.execute(stmt)
        count = result.scalar_one_or_none()
        return int(count or 0)
