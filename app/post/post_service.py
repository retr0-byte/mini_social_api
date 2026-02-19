from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.ext.asyncio.session import AsyncSession

from app.post.exceptions import PostDoesNotExist
from app.post.schemas import PostSchema, PostRequestSchema, PostDTO, AuthorDTO, PostIdDTO
from app.repositories import AuthenticationRepository
from app.repositories.like_repo import LikeRepository
from app.core.base_service import BaseService
from app.db.models import User, Post
from app.repositories.post_repo import PostRepository


class PostService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.post_repo = PostRepository(session=self.session)
        self.like_repo = LikeRepository(session=self.session)
        self.user_repo = AuthenticationRepository(session=self.session)

    async def get_posts(self, data: PostRequestSchema) -> List[PostDTO]:
        posts: List[PostDTO] = await self.post_repo.get_posts(
            limit=data.limit,
            offset=data.offset,
            user_id=data.user_id
        )

        return posts

    async def get_post(self, post: Post) -> PostDTO:
        user: Optional[User] = await self.user_repo.get_by_id(item_id=post.user_id)

        if not user:
            raise PostDoesNotExist()

        likes_count: int = await self.like_repo.get_likes_count(post_id=post.id)

        author: AuthorDTO = AuthorDTO(
            id=post.user_id,
            email=user.email
        )

        return PostDTO(
            title=post.title,
            content=post.content,
            author=author,
            likes_count=likes_count,
        )

    async def create_post(self, data: PostSchema, user: User) -> PostIdDTO:
        new_post: Post = await self.post_repo.create_post(
            title=data.title,
            content=data.content,
            user_id=user.id)

        return PostIdDTO(id=new_post.id)

    async def update_post(self, data: PostSchema, post: Post) -> PostSchema:
        updated_post: Post = await self.post_repo.update_post(
            post=post,
            title=data.title,
            content=data.content
        )

        return PostSchema(
            title=updated_post.title,
            content=updated_post.content
        )

    async def delete_post(self, post: Post):
        await self.post_repo.update_post(
            post=post,
            deleted_at=datetime.now(timezone.utc)
        )


