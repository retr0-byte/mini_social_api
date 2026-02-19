from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import Post
from app.db.session import get_db
from app.post.post_service import PostService
from app.post.dependencies import get_post_for_update, get_post_or_error
from app.post.schemas import PostRequestSchema, PostSchema, PostDTO, PostIdDTO
from app.schemas import ApiResponse


post_router = APIRouter(tags=['posts'])


@post_router.get(path="/posts", response_model=ApiResponse[List[Optional[PostDTO]]], status_code=200)
async def get_posts(
        params: PostRequestSchema = Depends(),
        session: AsyncSession = Depends(get_db)
) -> ApiResponse[List[Optional[PostDTO]]]:
    """
        View all posts or a specific user.

        Args:
        - params: Pagination params(limit, offset), user id.
        - session: Async database session.

        Returns:
        - 200: Posts data.

        Errors:
        - 400: Validation error (e.g., not pagination params).
    """
    posts_list: List[PostDTO] = await PostService(session=session).get_posts(data=params)

    return ApiResponse(data=posts_list)


@post_router.get(path="/post/{post_id}", response_model=ApiResponse[PostDTO], status_code=200)
async def read_post(
        post_id: int,
        post: Post = Depends(get_post_or_error),
        session: AsyncSession = Depends(get_db)
) -> ApiResponse[PostDTO]:
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
    post: PostDTO = await PostService(session=session).get_post(post)

    return ApiResponse(data=post)


@post_router.post(path="/post", response_model=ApiResponse[PostIdDTO], status_code=201)
async def write_post(
        data: PostSchema,
        session: AsyncSession = Depends(get_db),
        user=Depends(get_current_user)
) -> ApiResponse[PostIdDTO]:
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
    new_post_id: PostIdDTO = await PostService(session=session).create_post(data=data, user=user)

    return ApiResponse(data=new_post_id)


@post_router.patch(path="/post/{post_id}", response_model=ApiResponse[PostSchema], status_code=200)
async def update_post(
        data: PostSchema,
        post_id: int,
        session: AsyncSession = Depends(get_db),
        post: Post = Depends(get_post_for_update),
        user=Depends(get_current_user)
) -> ApiResponse[PostSchema]:
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
    updated_post: PostSchema = await PostService(session=session).update_post(data=data, post=post)

    return ApiResponse(data=updated_post)


@post_router.delete(path="/post/{post_id}", status_code=204)
async def delete_post(
        post_id: int,
        post: Post = Depends(get_post_for_update),
        user=Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
) -> None:
    """
        Delete post.

        Args:
        - post_id: ID post.
        - session: Async database session.
        - post: Post data from the database.
        - user: User data from the database.

        Returns:
        - 204: OK.

        Errors:
        - 401: User does not exist or missing ... token.
        - 403: You are not allowed to update a post.
        - 404: Post does not exist.
    """
    await PostService(session=session).delete_post(post=post)

