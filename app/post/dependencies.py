from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import Post
from app.db.session import get_db
from app.post.exceptions import PostDoesNotExist, PostUpdateForbidden
from app.repositories.post_repo import PostRepository


async def get_post_for_update(
    post_id: int,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> Post:
    post = await PostRepository().read_post_for_id(session=session, post_id=post_id)
    post = post.get('post')

    if not post:
        raise PostDoesNotExist()

    if post.user_id != user.user_id:
        raise PostUpdateForbidden()

    return post


async def get_post_or_error(
    post_id: int,
    session: AsyncSession = Depends(get_db),
) -> Post:
    post = await PostRepository().read_post_for_id(session=session, post_id=post_id)
    post = post.get('post')

    if not post:
        raise PostDoesNotExist()

    return post