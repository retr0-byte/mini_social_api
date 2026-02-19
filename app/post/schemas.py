from typing import Optional

from pydantic import BaseModel, Field


class PostRequestSchema(BaseModel):
    user_id: int | None = None
    limit: int = Field(gt=0, le=100)
    offset: int = Field(ge=0)


class PostSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class AuthorDTO(BaseModel):
    id: int
    email: Optional[str] = None


class PostDTO(BaseModel):
    title: str
    content: str
    author: AuthorDTO
    likes_count: Optional[int] = Field(ge=0)


class PostIdDTO(BaseModel):
    id: int




