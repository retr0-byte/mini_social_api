from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, EmailStr


class UserCredentialsSchema(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=6, max_length=32)


class UserSessionSchema(BaseModel):
    token_hash: bytes
    user_id: int
    expires_at: datetime


class TokenSubjectDTO(BaseModel):
    sub: str


class TokenDTO(BaseModel):
    token: str = Field(max_length=255)
    token_type: Literal["access", "refresh"]
    expires_at: datetime


class AuthTokensDTO(BaseModel):
    access_token: TokenDTO
    refresh_token: TokenDTO