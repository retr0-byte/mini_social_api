from typing import Literal

from app.core.base_exception import AppError


class UserAlreadyExist(AppError):
    status_code = 409
    detail='The user already exists.'


class UserDoesNotExist(AppError):
    status_code = 401
    detail='User does not exist'


class InvalidCredentials(AppError):
    status_code = 401
    detail='Invalid email or password'


class InvalidToken(AppError):
    status_code = 401

    def __init__(self, token_type: Literal["access", "refresh"]) -> None:
        super().__init__(detail=f"Missing {token_type} token")


class NotAuthenticated(AppError):
    status_code = 401
    detail="User not authenticated"
