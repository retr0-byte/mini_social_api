from typing import Text
from pydantic import BaseModel, Field


class PostRequestSchema(BaseModel):
    author_id: int | None
    limit: int = Field(gt=0, le=100)
    offset: int = Field(ge=0)
    with_likes: bool = False


class PostSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

