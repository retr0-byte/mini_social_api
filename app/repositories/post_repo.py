from datetime import datetime
from typing import Optional, Sequence, Any

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Post, User
from app.db.models.post_likes import PostLikes
from app.post.exceptions import PostDoesNotExist


class PostRepository:
    async def create_post(self,
                          session: AsyncSession,
                          title: str,
                          content: str,
                          user_id: int) -> Post:
        try:
            new_post = Post(title=title, content=content, user_id=user_id)
            session.add(new_post)

            await session.commit()
            await session.refresh(new_post)

            return new_post
        except Exception:
            await session.rollback()
            raise

    async def read_post_for_id(self,
                               session: AsyncSession,
                               post_id: int) -> Any:
        stmt = (
            select(Post, User.email.label("user_email"))
            .join(User, Post.user_id == User.user_id)
            .where(Post.post_id == post_id)
        )

        likes_subquery = (
            select(func.count(PostLikes.like_id))
            .where(PostLikes.post_id == Post.post_id)
            .scalar_subquery()
            .correlate(Post)
        )
        stmt = stmt.add_columns(likes_subquery.label("likes_count"))

        result = await session.execute(stmt)
        row = result.one_or_none()

        if row:
            post = row.Post
            return {
                "post": post,
                "user_email": row.user_email,
                "likes_count": row.likes_count
            }
        return None

    async def get_posts(self,
                        session: AsyncSession,
                        limit: int,
                        offset: int,
                        with_likes: bool,
                        user_id: Optional[int] = None,
                        ) -> Sequence[Any]:
        stmt = select(Post)

        if user_id:
            stmt = stmt.where(Post.user_id == user_id)

        if with_likes:
            likes_subquery = (
                select(func.count(PostLikes.like_id))
                .where(PostLikes.post_id == Post.post_id)
                .scalar_subquery()
                .correlate(Post)
            )
            stmt = stmt.add_columns(likes_subquery.label("likes_count"))

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)

        if with_likes:
            return result.all()

        return result.scalars().all()

    async def update_post(self,
                          session: AsyncSession,
                          post_id: int,
                          title: str = None,
                          content: str = None,
                          deleted_at: datetime = None,
                          ):

        select_stmt = select(Post).where(Post.post_id == post_id)
        query = await session.execute(select_stmt)
        update_account = query.scalar()

        if not update_account:
            raise PostDoesNotExist(f"Account with id {post_id} does not exist!")

        update_stmt = update(table=Post).where(Post.post_id == update_account.post_id)

        if title:
            update_stmt = update_stmt.values(title=title)

        if content:
            update_stmt = update_stmt.values(content=content)

        if deleted_at:
            update_stmt = update_stmt.values(deleted_at=deleted_at)

        await session.execute(statement=update_stmt)
        await session.commit()
        await session.refresh(instance=update_account)

        return update_account


