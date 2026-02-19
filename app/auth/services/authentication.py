from typing import Optional

from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.exceptions import UserDoesNotExist, InvalidCredentials
from app.auth.schemas import UserCredentialsSchema, UserSessionSchema, AuthTokensDTO, TokenDTO, TokenSubjectDTO
from app.core.base_service import BaseService
from app.db.models import User, UserSession
from app.repositories import AuthenticationRepository
from app.auth.utils import verify_secret, hash_token
from app.auth.services.jwt_service import JwtService


class AuthenticationService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.user_repo = AuthenticationRepository(self.session)

    async def _verified_credentials(
            self,
            *,
            user: Optional[User],
            password: str
    ) -> None:

        if not user:
            raise UserDoesNotExist()

        if not verify_secret(
                value=password,
                hashed_value=user.password
        ):
            raise InvalidCredentials()

    async def _revoke_session(self, user: User) -> None:
        active_session: UserSession = await self.user_repo.read_active_session_by_user_id(user_id=user.id)

        if active_session:
            await self.user_repo.revoke_session(user_session=active_session)

    async def _create_tokens(self, user: User) -> AuthTokensDTO:
        token_subject = TokenSubjectDTO(sub=str(user.id))

        jwt_service = JwtService()
        access_token: TokenDTO = await jwt_service.create_access_token(data=token_subject)
        refresh_token: TokenDTO = await jwt_service.create_refresh_token(data=token_subject)

        return AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def authenticate_user(self, data: UserCredentialsSchema) -> AuthTokensDTO:
        user: Optional[User] = await self.user_repo.read_user_for_email(email=data.email) # noqa

        await self._verified_credentials(user=user, password=data.password)
        await self._revoke_session(user=user)

        tokens: AuthTokensDTO = await self._create_tokens(user=user)

        _hash_token: bytes = hash_token(token=tokens.refresh_token.token)
        new_token_data: UserSessionSchema = UserSessionSchema(
            token_hash=_hash_token,
            user_id=user.id,  # noqa
            expires_at=tokens.refresh_token.expires_at
        )

        await self.user_repo.create_user_session(data=new_token_data)

        return tokens

    async def logout_user(self, user: User):
        user_session: Optional[UserSession] = await self.user_repo.read_active_session_by_user_id(user_id=user.id)
        if user_session:
            await self.user_repo.revoke_session(user_session=user_session)
