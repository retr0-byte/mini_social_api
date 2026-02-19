from datetime import datetime, timezone, timedelta
from typing import Literal, Dict, Any, Optional

from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.exceptions import InvalidToken, NotAuthenticated
from app.auth.schemas import TokenDTO, TokenSubjectDTO
from app.config import Settings
from app.core.dependencies import get_settings
from app.db.models import UserSession
from app.repositories import AuthenticationRepository

TokenType = Literal["access", "refresh"]


class JwtService:
    def __init__(self):
        self.settings: Settings = get_settings()

    def _create_token(
            self,
            secret_key: str,
            jwt_algorithm: str,
            payload: Dict[str, str | datetime]
    ) -> str:

        token: str = jwt.encode(
            claims=payload,
            key=secret_key,
            algorithm=jwt_algorithm
        )

        return token

    async def create_access_token(
            self,
            data: TokenSubjectDTO,
            expires_minutes: int = 15,
    ) -> TokenDTO:

        exp: datetime = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
        token_type: TokenType = "access"

        payload: Dict[str, str | datetime] = {
            'sub': data.sub,
            'type': token_type,
            'exp': exp
        }

        secret_key: str = self.settings.jwt_access_key
        jwt_algorithm: str = self.settings.JWT_ALGORITHM

        token: str = self._create_token(
            secret_key=secret_key,
            jwt_algorithm=jwt_algorithm,
            payload=payload
        )

        return TokenDTO(
            token=token,
            token_type=token_type,
            expires_at=exp
        )

    async def create_refresh_token(
            self,
            data: TokenSubjectDTO,
            expires_days: int = 7,
    ) -> TokenDTO:
        exp: datetime = datetime.now(tz=timezone.utc) + timedelta(days=expires_days)
        token_type: TokenType = "refresh"

        payload: Dict[str, str | datetime] = {
            'sub': data.sub,
            'type': token_type,
            'exp': exp
        }

        secret_key: str = self.settings.jwt_refresh_key
        jwt_algorithm: str = self.settings.JWT_ALGORITHM

        token: str = self._create_token(
            secret_key=secret_key,
            jwt_algorithm=jwt_algorithm,
            payload=payload
        )

        return TokenDTO(
            token=token,
            token_type=token_type,
            expires_at=exp
        )

    async def refresh_access_token(self, token: str, session: AsyncSession) -> TokenDTO:
        verify_token: Dict[str, Any] = await self.verify_refresh_token(token=token, session=session)
        access_token: TokenDTO = await self.create_access_token(data=TokenSubjectDTO(sub=verify_token['sub']))

        return access_token

    def _verify_token(
            self,
            token: str,
            token_type: Literal['access', 'refresh']
    ) -> Dict[str, Any]:

        try:
             secret_key: str = self.settings.jwt_access_key if token_type == 'access' else self.settings.jwt_refresh_key

             payload: Dict[str, Any] = jwt.decode(
                token,
                secret_key,
                algorithms=self.settings.JWT_ALGORITHM,
            )
        except (ExpiredSignatureError, JWTError):
            raise InvalidToken(token_type=token_type)

        if payload.get("type") != token_type:
            raise InvalidToken(token_type=token_type)

        return payload

    async def verify_refresh_token(self, token: str, session: AsyncSession) -> Dict[str, Any]:
        payload: Dict[str, Any] = self._verify_token(
            token=token,
            token_type='refresh'
        )
        user_id: int = int(payload["sub"])

        active_session: Optional[UserSession] = await AuthenticationRepository(
            session=session
        ).read_active_session_by_user_id(user_id=user_id)

        if not active_session:
            raise NotAuthenticated()

        if not payload:
            raise InvalidToken(token_type='refresh')

        return payload

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        payload: Dict[str, Any] = self._verify_token(
            token=token,
            token_type='access'
        )

        if not payload:
            raise InvalidToken(token_type="access")

        sub: str = payload.get("sub")
        if not sub:
            raise InvalidToken(token_type="access")

        try:
            user_id: int = int(sub)
        except (TypeError, ValueError):
            raise InvalidToken(token_type="access")


        return payload