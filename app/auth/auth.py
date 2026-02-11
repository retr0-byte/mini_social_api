from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.auth.auth_service import RegistrationService, AuthoriseService, JwtService
from app.auth.dependencies import get_current_user, get_refresh_token_from_cookie
from app.auth.schemas import UserCredentialsSchema
from app.db.session import get_db
from app.db.models import User

auth_router = APIRouter(prefix="/auth", tags=['auth'])


@auth_router.post("/signup")
async def signup(data: UserCredentialsSchema,
                 session: AsyncSession = Depends(get_db)):
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
    reg_user = await RegistrationService(session=session).register_user(data=data)

    return JSONResponse(
        status_code=201,
        content=reg_user
    )


@auth_router.post("/signin")
async def signin(data: UserCredentialsSchema,
                 session: AsyncSession = Depends(get_db)):
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
    access_token, refresh_token = await AuthoriseService(session=session).authenticate_user(data=data)

    resp = JSONResponse(
        status_code=200,
        content='OK',
    )

    resp.set_cookie(
        key="rt",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/auth/refresh",
        max_age=60 * 60 * 24 * 7,
    )
    resp.set_cookie(
        key="at",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 15,
    )

    return resp


@auth_router.post("/refresh")
async def change_token(refresh_token: str = Depends(get_refresh_token_from_cookie),
                       session: AsyncSession = Depends(get_db)):
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
    jwt_service = JwtService()

    verify_token = await jwt_service.verify_refresh_token(token=refresh_token, session=session)
    access_token = await jwt_service.create_access_token(
        data={"sub": str(verify_token['sub'])})

    resp = JSONResponse(
        status_code=200,
        content='OK',
    )

    resp.set_cookie(
        key="at",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=60 * 15,
    )

    return resp


@auth_router.post("/logout")
async def logout(user: User = Depends(get_current_user),
                 session: AsyncSession = Depends(get_db)):
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
    await AuthoriseService(session=session).logout_user(user=user)

    resp = JSONResponse(
        status_code=200,
        content='OK'
    )
    resp.delete_cookie(key="rt", path="/auth/refresh", samesite="lax")
    resp.delete_cookie(key="at", path="/", samesite="lax")

    return resp