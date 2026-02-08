from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class UserCredentialsSchema(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=6, max_length=32)

class UserSessionSchema(BaseModel):
    token_hash: bytes
    user_id: int
    expires_at: datetime