from datetime import datetime
from typing import Optional, Sequence, List

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Post
from app.db.models.post_likes import PostLikes
from app.post.exceptions import PostDoesNotExist
from app.post.schemas import PostDTO, AuthorDTO
from app.repositories.base_repo import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Post)

    async def create_post(
            self,
            title: str,
            content: str,
            user_id: int
    ) -> Post:
        try:
            new_post: Post = Post(title=title, content=content, user_id=user_id)
            self.session.add(new_post)

            await self.session.commit()
            await self.session.refresh(new_post)

            return new_post
        except Exception:
            await self.session.rollback()
            raise

    async def get_posts(
            self,
            limit: int,
            offset: int,
            user_id: Optional[int] = None,
    ) -> List[PostDTO]:

        stmt = select(Post).where(Post.deleted_at == None)

        if user_id is not None:
            stmt = stmt.where(Post.user_id == user_id)

        likes_count_sq = (
            select(func.count(PostLikes.id))
            .where(PostLikes.post_id == Post.id)
            .scalar_subquery()
        )

        stmt = (
            stmt.add_columns(likes_count_sq.label("likes_count"))
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        rows: Sequence[tuple[Post, int]] = result.tuples().all()
        return [
            PostDTO(
                title=post.title,
                content=post.content,
                author=AuthorDTO(id=post.user_id),
                likes_count=int(likes_count),
            )
            for post, likes_count in rows
        ]

    async def update_post(
            self,
            post: Post,
            title: str = None,
            content: str = None,
            deleted_at: datetime = None,
    ) -> Post:
        update_post: Post = post

        if not update_post:
            raise PostDoesNotExist()

        update_stmt = update(table=Post).where(Post.id == update_post.id)

        if title:
            update_stmt = update_stmt.values(title=title)

        if content:
            update_stmt = update_stmt.values(content=content)

        if deleted_at:
            update_stmt = update_stmt.values(deleted_at=deleted_at)

        await self.session.execute(statement=update_stmt)
        await self.session.commit()
        await self.session.refresh(instance=update_post)

        return update_post


