from fastapi import Response, APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.services import RegistrationService, AuthenticationService, JwtService

from app.auth.dependencies import get_current_user, get_refresh_token_from_cookie
from app.auth.schemas import UserCredentialsSchema, AuthTokensDTO, TokenDTO
from app.db.session import get_db
from app.db.models import User
from app.schemas import ApiResponse


auth_router = APIRouter(prefix="/auth", tags=['auth'])


@auth_router.post(path="/signup", response_model=ApiResponse[str], status_code=201)
async def signup(
        data: UserCredentialsSchema,
        session: AsyncSession = Depends(get_db)
) -> ApiResponse[str]:
    """
        Register a new user.

        Args:
        - data: User credentials (email, password).
        - session: Async database session.

        Returns:
        - 201: User successfully registered.

        Errors:
        - 400: Validation error (e.g., weak password, invalid email format).
        - 409: The user already exists.
    """
    await RegistrationService(session=session).register_user(data=data)

    return ApiResponse(data='User successfully registered')


@auth_router.post(path="/signin", response_model=ApiResponse[str], status_code=200)
async def signin(
        response: Response,
        data: UserCredentialsSchema,
        session: AsyncSession = Depends(get_db),
) -> ApiResponse[str]:
    """
        User authorization.

        Args:
        - data: User credentials (email, password).
        - session: Async database session.

        Returns:
        - 200: User successfully authorized. (set refresh and access token as rt and at).

        Errors:
        - 400: Validation error (e.g., weak password, invalid email format).
        - 401: User does not exist or invalid email or password.
    """
    tokens: AuthTokensDTO = await AuthenticationService(session=session).authenticate_user(data=data)
    refresh_token: TokenDTO = tokens.refresh_token
    access_token: TokenDTO = tokens.access_token

    response.set_cookie(
        key="rt",
        value=refresh_token.token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth/refresh",
        max_age=60 * 60 * 24 * 7,
    )
    response.set_cookie(
        key="at",
        value=access_token.token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 15,
    )

    return ApiResponse(data='OK')


@auth_router.post(path="/refresh", response_model=ApiResponse[str], status_code=200)
async def change_token(
        response: Response,
        refresh_token: str = Depends(get_refresh_token_from_cookie),
        session: AsyncSession = Depends(get_db)
) -> ApiResponse[str]:
    """
        Access token renewal.

        Args:
        - refresh_token: Obtaining a refresh token from a cookie.
        - session: Async database session.

        Returns:
        - 200: OK. (set new access token as at).

        Errors:
        - 401: User not authenticated or Invalid ... token.
    """
    new_access_token: TokenDTO = await JwtService().refresh_access_token(token=refresh_token, session=session)

    response.set_cookie(
        key="at",
        value=new_access_token.token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 15,
    )

    return ApiResponse(data='OK')


@auth_router.post(path="/logout", response_model=ApiResponse[str], status_code=200)
async def logout(
        response: Response,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
) -> ApiResponse[str]:
    """
        Logout.

        Args:
        - user: User data from the database.
        - session: Async database session.

        Returns:
        - 200: OK. (set new access token as at).

        Errors:
        - 401: User does not exist or missing ... token.
    """
    await AuthenticationService(session=session).logout_user(user=user)

    response.delete_cookie(key="rt", path="/auth/refresh", samesite="lax")
    response.delete_cookie(key="at", path="/", samesite="lax")

    return ApiResponse(data='OK')