from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import Post, User
from app.db.session import get_db
from app.post.exceptions import PostDoesNotExist, PostUpdateForbidden
from app.repositories.post_repo import PostRepository


async def get_post_or_error(
    post_id: int,
    session: AsyncSession = Depends(get_db),
) -> Post:
    post: Post = await PostRepository(session=session).get_by_id(item_id=post_id)

    if not post:
        raise PostDoesNotExist()

    return post


async def get_post_for_update(
    post_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    post: Post = Depends(get_post_or_error)
) -> Post:

    if post.user_id != user.id:
        raise PostUpdateForbidden()

    return post
