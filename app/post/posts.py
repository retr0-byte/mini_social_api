from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.auth_service import get_current_user
from app.db.models import Post
from app.db.session import get_db
from app.post.post_service import PostService, get_post_for_update
from app.post.schemas import PostRequestSchema, PostSchema

post_router = APIRouter(tags=['posts'])


@post_router.get("/posts")
async def posts(params: PostRequestSchema = Depends(),
                session: AsyncSession = Depends(get_db)):
    """
        View all posts or a specific user.

        Args:
        - params: Pagination params(limit, offset), user id, with likes.
        - session: Async database session.

        Returns:
        - 200: Posts data.

        Errors:
        - 400: Validation error (e.g., not pagination params).
    """
    posts = await PostService(session=session).get_posts(data=params)

    return JSONResponse(
        status_code=200,
        content=posts
    )


@post_router.get("/post/{post_id}")
async def read_post(post_id: int,
                    session: AsyncSession = Depends(get_db)):
    """
        View a specific post.

        Args:
        - post_id: ID post.
        - session: Async database session.

        Returns:
        - 200: Post data.

        Errors:
        - 404: Post does not exist.
    """
    post = await PostService(session=session).get_post(post_id)

    return JSONResponse(
        status_code=200,
        content=post
    )


@post_router.post("/post")
async def write_post(data: PostSchema,
                     session: AsyncSession = Depends(get_db),
                     user=Depends(get_current_user)):
    """
        Write post.

        Args:
        - data: data params (title, content).
        - session: Async database session.
        - user: User data from the database and.

        Returns:
        - 201: ID post

        Errors:
        - 400: Validation error (e.g., not title or content incorrect number of characters).
        - 401: User does not exist or missing ... token.
    """
    new_post = await PostService(session=session).create_post(data=data, user=user)

    return JSONResponse(
        status_code=201,
        content=new_post
    )


@post_router.patch("/post/{post_id}")
async def update_post(data: PostSchema,
                      post_id: int,
                      session: AsyncSession = Depends(get_db),
                      post: Post = Depends(get_post_for_update),
                      user=Depends(get_current_user)):
    """
        Update post.

        Args:
        - data: data params (title, content).
        - post_id: ID post.
        - session: Async database session.
        - post: Post data from the database.
        - user: User data from the database.

        Returns:
        - 200: ID post and update column.

        Errors:
        - 400: Validation error (e.g., not title or content incorrect number of characters).
        - 401: User does not exist or missing ... token.
        - 403: You are not allowed to update a post.
        - 404: Post does not exist.
    """
    updated_post = await PostService(session=session).update_post(data=data, post=post)

    return JSONResponse(
        status_code=200,
        content=updated_post
    )


@post_router.delete("/post/{post_id}")
async def delete_post(post_id: int,
                      post: Post = Depends(get_post_for_update),
                      user=Depends(get_current_user),
                      session: AsyncSession = Depends(get_db)):
    """
        Delete post.

        Args:
        - post_id: ID post.
        - session: Async database session.
        - post: Post data from the database.
        - user: User data from the database.

        Returns:
        - 204: Nothing is returned.

        Errors:
        - 401: User does not exist or missing ... token.
        - 403: You are not allowed to update a post.
        - 404: Post does not exist.
    """
    await PostService(session=session).delete_post(post=post)

    return JSONResponse(
        status_code=204,
        content=None
    )
