from typing import Dict, Any

from app.services.base import BaseService
from ..repositories.like_repo import LikeRepository


class LikesService(BaseService):
    async def create_post_like(self, post_id: int, user_id: int):
        await LikeRepository().create_post_like(session=self.session,
                                                post_id=post_id,
                                                user_id=user_id)

