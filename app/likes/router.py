from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.db.models import Post
from app.db.session import get_db
from app.likes.likes_service import LikesService
from app.post.dependencies import get_post_or_error
from app.auth.dependencies import get_current_user
from app.schemas import ApiResponse


like_router = APIRouter(tags=['likes'])


@like_router.post(path="/like/{post_id}", response_model=ApiResponse[str], status_code=200)
async def like(
        post_id: int,
        session: AsyncSession = Depends(get_db),
        post: Post = Depends(get_post_or_error),
        user=Depends(get_current_user)
):
    """
        Like a post (idempotent).

        Args:
            post_id: post ID.
            session: Async database session.
            post: Post data from the database.
            user: User data from the database.

        Behavior:
        - If the like does not exist -> creates it.
        - If the like already exists -> no-op.

        Returns:
        - 200: like exists after the call (created or already existed).

        Errors:
        - 401: user is not authenticated or invalid token or user does not exist.
        - 404: post does not exist.

        Concurrency:
        - Guaranteed by DB unique constraint (post_id, user_id).
    """

    await LikesService(session=session).post_like(post=post, user=user)

    return ApiResponse(data='OK')


@like_router.delete(path="/like/{post_id}", response_model=ApiResponse[str], status_code=200)
async def unlike(
        post_id: int,
        session: AsyncSession = Depends(get_db),
        post: Post = Depends(get_post_or_error),
        user=Depends(get_current_user)
):
    """
        Unlike a post (idempotent).

        Args:
            post_id: post ID.
            session: Async database session.
            post: Post data from the database.
            user: User data from the database.

        Behavior:
        - If the like does not exist -> no-op.
        - If the like exists -> delete it.

        Returns:
        - 200: like does not exist after the call (deleted).

        Errors:
        - 401: user is not authenticated or invalid token or user does not exist.
        - 404: post does not exist.
    """
    await LikesService(session=session).post_unlike(post=post, user=user)

    return ApiResponse(data='OK')
