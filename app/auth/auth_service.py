import hashlib
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Literal
from jose import jwt, JWTError, ExpiredSignatureError
import bcrypt

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.exceptions import UserDoesNotExist, InvalidCredentials, InvalidToken, NotAuthenticated, UserAlreadyExist
from app.auth.schemas import UserCredentialsSchema, UserSessionSchema
from app.config import Settings
from app.db.models import User
from app.repositories import AuthenticationRepository
from app.services.base import BaseService


class RegistrationService(BaseService):
    async def _hash_password(self, password: str):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed

    async def register_user(self, data: UserCredentialsSchema) -> Dict[str, Any]:
        email = str(data.email)
        password = data.password
        hashed_password = await self._hash_password(password)

        try:
            await AuthenticationRepository().create_user(session=self.session,
                                                 email=email,
                                                 password=hashed_password)
        except IntegrityError:
            raise UserAlreadyExist()

        data_for_response = {
            'message': 'User successfully registered',
        }

        return await self._create_response(data=data_for_response)


class AuthoriseService(BaseService):
    async def _verification_password(self, hashed_password: bytes, password: str) -> bool:
        verification = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        return verification

    async def authenticate_user(self, data: UserCredentialsSchema) -> Tuple[str, str]:
        email = str(data.email)
        password = data.password

        user = await AuthenticationRepository().read_user_for_email(
            session=self.session,
            email=email
        )
        if not user:
            raise UserDoesNotExist()

        if not await self._verification_password(
                password=password,
                hashed_password=user.password
        ):
            raise InvalidCredentials()

        jwt_service = JwtService()
        access_token =  await jwt_service.create_access_token(data={"sub": str(user.user_id)})

        active_session = await AuthenticationRepository().read_active_session_by_user_id(session=self.session,
                                                                                         user_id=user.user_id)
        if active_session:
            await AuthenticationRepository().revoke_session(session=self.session, user_session=active_session)

        exp, refresh_token = await jwt_service.create_refresh_token(data={"sub": str(user.user_id)})
        hash_token = jwt_service.hash_refresh_token(token=refresh_token)

        new_token_data = UserSessionSchema(
            token_hash=hash_token,
            user_id=user.user_id,
            expires_at=exp
        )

        await AuthenticationRepository().create_user_session(session=self.session, data=new_token_data)

        return access_token, refresh_token

    async def logout_user(self, user: User):
        auth_repository = AuthenticationRepository()
        user_session = await auth_repository.read_active_session_by_user_id(user_id=user.user_id,
                                                                            session=self.session)

        await auth_repository.revoke_session(session=self.session, user_session=user_session)


class JwtService:
    settings = Settings()

    def hash_refresh_token(self, token: str) -> bytes:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        return bcrypt.hashpw(digest, bcrypt.gensalt())

    def _verification_token(self, hashed_token: bytes, token: str) -> bool:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        return bcrypt.checkpw(digest, hashed_token)


    async def create_access_token(self, data: dict, expires_minutes: int = 15) -> str:
        payload = data.copy()
        payload['type'] = "access"
        payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)

        return jwt.encode(payload,
                          self.settings.JWT_ACCESS_SECRET_KEY.get_secret_value(),
                          algorithm=self.settings.JWT_ALGORITHM)

    async def create_refresh_token(self, data: dict, expires_days: int = 7) -> Tuple[datetime, str]:
        payload = data.copy()
        exp = datetime.now(tz=timezone.utc) + timedelta(days=expires_days)
        payload['type'] = "refresh"
        payload["exp"] = exp

        return exp, jwt.encode(payload,
                          self.settings.JWT_REFRESH_SECRET_KEY.get_secret_value(),
                          algorithm=self.settings.JWT_ALGORITHM)

    def verify_token(self, token: str, token_type: Literal['access', 'refresh']) -> Dict[str, Any]:
        try:
            secret_key = self.settings.JWT_ACCESS_SECRET_KEY.get_secret_value()\
                if token_type == 'access' else self.settings.JWT_REFRESH_SECRET_KEY.get_secret_value()

            payload = jwt.decode(
                token,
                secret_key,
                algorithms=self.settings.JWT_ALGORITHM,
            )
        except (ExpiredSignatureError, JWTError):
            traceback.print_exc()
            raise InvalidToken(token_type=token_type)

        if payload.get("type") != token_type:
            raise InvalidToken(token_type=token_type)

        return payload

    async def verify_refresh_token(self, token: str, session: AsyncSession) -> Dict[str, Any]:
        payload = self.verify_token(token=token, token_type='refresh')
        user_id = int(payload["sub"])

        active_session = await AuthenticationRepository().read_active_session_by_user_id(session=session, user_id=user_id)

        if not active_session:
            raise NotAuthenticated()

        if not self._verification_token(hashed_token=active_session.token_hash, token=token):
            raise InvalidToken(token_type='refresh')

        return payload






