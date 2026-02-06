from app.services.base import BaseService
from ..repositories.like_repo import LikeRepository


class LikesService(BaseService):
    async def post_like(self, post_id: int, user_id: int):
        await LikeRepository().post_like(
            session=self.session,
            post_id=post_id,
            user_id=user_id
        )

    async def post_unlike(self, post_id: int, user_id: int):
        await LikeRepository().post_unlike(
            session=self.session,
            post_id=post_id,
            user_id=user_id
        )

