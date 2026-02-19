from datetime import datetime, timezone
from sqlite3 import IntegrityError
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import UserAlreadyExist
from app.auth.schemas import UserCredentialsSchema, UserSessionSchema
from app.db.models import User, UserSession
from app.repositories.base_repo import BaseRepository


class AuthenticationRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def create_user(
            self,
            email: str,
            password: bytes
    ) -> None:
        try:
            new_user = User(email=email, password=password)
            self.session.add(new_user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExist()
        except Exception:
            await self.session.rollback()
            raise

    async def read_user_for_email(
            self,
            email: str
    ) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def read_active_session_by_user_id(
            self,
            user_id: int
    ) -> Optional[UserSession]:
        stmt = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user_session(
            self,
            data: UserSessionSchema
    ) -> None:
        try:
            new_user_session = UserSession(
                user_id=data.user_id,
                token_hash=data.token_hash,
                expires_at=data.expires_at
            )
            self.session.add(new_user_session)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise


    async def revoke_session(
            self,
            user_session: UserSession
    ) -> None:
        if user_session.revoked_at is not None:
            return

        user_session.revoked_at = datetime.now(timezone.utc)
        await self.session.commit()