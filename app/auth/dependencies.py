from typing import Optional

from fastapi import Depends, Cookie
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.services import JwtService
from app.auth.exceptions import UserDoesNotExist, InvalidToken
from app.db.models import User
from app.db.session import get_db
from app.repositories import AuthenticationRepository


def get_access_token_from_cookie(access_token: Optional[str] = Cookie(default=None, alias='at')) -> str:
    if not access_token:
        raise InvalidToken(token_type='access')

    return access_token


def get_refresh_token_from_cookie(refresh_token: Optional[str] = Cookie(default=None, alias='rt')) -> str:
    if not refresh_token:
        raise InvalidToken(token_type='refresh')
    return refresh_token


def get_current_user_id(token: str = Depends(get_access_token_from_cookie)) -> int:
    payload = JwtService().verify_access_token(token=token)

    try:
        sub = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise InvalidToken(token_type='access')
    if sub <= 0:
        raise InvalidToken(token_type="access")

    return sub


async def get_current_user(
        session: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
) -> Optional[User]:
    user = await AuthenticationRepository(session=session).get_by_id(item_id=user_id)
    if not user:
        raise UserDoesNotExist()

    return user
