from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession


from app.db.models import Post
from app.db.session import get_db
from app.likes.likes_service import LikesService
from app.post.post_service import get_post_or_error
from app.auth.auth_service import get_current_user


like_router = APIRouter(tags=['likes'])


@like_router.post("/like/{post_id}")
async def like(
        post_id: int,
        session: AsyncSession = Depends(get_db),
        post: Post = Depends(get_post_or_error),
        user=Depends(get_current_user)
):
    """
        Like a post (idempotent).

        Behavior:
        - If the like does not exist -> creates it.
        - If the like already exists -> no-op.

        Responses:
        - 200: like exists after the call (created or already existed)
        - 401: user is not authenticated or invalid token
        - 404: post does not exist

        Concurrency:
        - Guaranteed by DB unique constraint (post_id, user_id).
    """

    await LikesService(session=session).post_like(post_id=post.post_id, user_id=user.user_id)

    return JSONResponse(
        status_code=200,
        content='OK'
    )

@like_router.delete("/like/{post_id}")
async def unlike(
        post_id: int,
        session: AsyncSession = Depends(get_db),
        post: Post = Depends(get_post_or_error),
        user=Depends(get_current_user)
):
    """
        Unlike a post (idempotent).

        Behavior:
        - If the like does not exist -> no-op.
        - If the like exists -> delete it.

        Responses:
        - 200: like does not exist after the call (deleted)
        - 401: user is not authenticated or invalid token
        - 404: post does not exist
    """
    await LikesService(session=session).post_unlike(post_id=post.post_id, user_id=user.user_id)

    return JSONResponse(
        status_code=200,
        content='OK'
    )
