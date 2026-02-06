from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PostLikes


class LikeRepository:
    async def post_like(self,
                          session: AsyncSession,
                          post_id: int,
                          user_id: int):
        try:
            new_post_like = PostLikes(post_id=post_id, user_id=user_id)
            session.add(new_post_like)
            await session.commit()
        except IntegrityError:
            await session.rollback()

    async def post_unlike(self, session: AsyncSession,
                               post_id: int,
                               user_id: int):
        await session.execute(
            delete(PostLikes).where(
                PostLikes.post_id == post_id,
                PostLikes.user_id == user_id,
            )
        )

        await session.commit()