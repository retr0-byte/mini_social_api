from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.functions import current_user

from app.db.session import get_db
from app.post.post_service import PostService
from app.post.schemas import PostRequestSchema, PostSchema


post_router = APIRouter(tags=['posts'])


@post_router.get("/posts")
async def posts(data: PostRequestSchema, session: AsyncSession = Depends(get_db)):
    posts = await PostService(session=session).get_posts(data)

    return JSONResponse(
        status_code=200,
        content=posts
    )

@post_router.get("/post/{post_id}")
async def read_post(post_id: int, session: AsyncSession = Depends(get_db)):
    post = await PostService(session=session).get_post(post_id)

    return JSONResponse(
        status_code=200,
        content=post
    )

# =============== Доделать проверку юзера ====================
@post_router.post("/post")
async def write_post(data: PostSchema, session: AsyncSession = Depends(get_db), current_user = Depends()):
    new_post = await PostService(session=session).create_post(data=data, user=current_user)

    return JSONResponse(
        status_code=201,
        content=new_post
    )


@post_router.patch("/post/{post_id}")
async def update_post(data: PostSchema, post_id: int, session: AsyncSession = Depends(get_db)):
    updated_post = await PostService(session=session).update_post(post_id=post_id, data=data)

    return JSONResponse(
        status_code=200,
        content=updated_post
    )


@post_router.delete("/post/{post_id}")
async def delete_post(post_id: int, session: AsyncSession = Depends(get_db)):
    await PostService(session=session).delete_post(post_id)

    return JSONResponse(
        status_code=204,
        content=None
    )
