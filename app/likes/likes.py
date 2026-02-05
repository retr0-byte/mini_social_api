from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.db.session import get_db
from app.likes.likes_service import LikesService


like_router = APIRouter(tags=['likes'])


@like_router.get("/like/{post_id}")
async def like(post_id: int, session: AsyncSession = Depends(get_db), user = ...):
    await LikesService(session=session).create_post_like(post_id=post_id, user_id=user.user_id)

    return JSONResponse(
        status_code=200,
        content='OK'
    )
