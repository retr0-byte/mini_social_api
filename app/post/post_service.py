from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import HTTPException

from .schemas import PostSchema, PostRequestSchema
from app.services.base import BaseService
from ..db.models import User
from ..repositories.post_repo import PostRepository


class PostService(BaseService):
    async def get_posts(self, data: PostRequestSchema) -> Dict[str, Any]:
        dict_data = data.model_dump(mode='python')
        db_posts = await PostRepository().get_posts(session=self.session,
                                                    **dict_data)

        normalized_posts_data = []
        for post in db_posts:
            post_data = {
                'title': post.title,
                'content': post.content,
                'author': {
                    'id': post.user_id,
                },
            }
            if data.with_likes:
                post_data['likes_count'] = post.likes_count


        return await self._create_response(
            data= {
                'posts': normalized_posts_data
            }
        )

    async def get_post(self, post_id: int) -> Dict[str, Any]:
        db_post = await PostRepository().read_post_for_id(session=self.session,
                                                          post_id=post_id)
        if not db_post:
            raise HTTPException(status_code=404, detail='Post not found')

        post_data = db_post["post"]

        normalized_post_data = {
            'title': post_data.title,
            'content': post_data.content,
            'author': {
                'id': post_data.user_id,
                'email': db_post["user_email"],
            },
            'likes_count': db_post["likes_count"],
        }

        return await self._create_response(
                data={
                    'post': normalized_post_data
                }
            )

    async def create_post(self, data: PostSchema, user: User) -> Dict[str, Any]:
        dict_data = data.model_dump(mode='python')
        new_post = await PostRepository().create_post(session=self.session,
                                                      **dict_data,
                                                      user_id=user.user_id)

        return await self._create_response(
            data={
                'id': new_post.post_id
            }
        )

    async def update_post(self, data: PostSchema, post_id: int) -> Dict[str, Any]:
        dict_data = data.model_dump(mode='python')
        updated_post = await PostRepository().update_post(session=self.session,
                                                          post_id=post_id,
                                                          **dict_data)

        return await self._create_response(
            data={
                'id': updated_post.post_id,
                'new_column': dict_data
            }
        )

    async def delete_post(self, post_id: int):
        await PostRepository().update_post(session=self.session,
                                           post_id=post_id,
                                           deleted_at=datetime.now(timezone.utc))


