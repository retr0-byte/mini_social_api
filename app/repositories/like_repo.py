from datetime import datetime, timezone
from typing import Optional, List, Sequence, Any, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PostLikes


class LikeRepository:
    async def create_post_like(self,
                          session: AsyncSession,
                          post_id: int,
                          user_id: int):
        try:
            new_post_like = PostLikes(post_id=post_id, user_id=user_id)
            session.add(new_post_like)
            await session.commit()
        except Exception:
            await session.rollback()