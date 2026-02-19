from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.base_service import BaseService
from app.db.models import Post, User
from app.repositories.like_repo import LikeRepository


class LikesService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.like_repo = LikeRepository(session=self.session)

    async def post_like(self, post: Post, user: User):
        await self.like_repo.post_like(
            post_id=post.id,
            user_id=user.id
        )

    async def post_unlike(self, post: Post, user: User):
        await self.like_repo.post_unlike(
            post_id=post.id,
            user_id=user.id
        )

