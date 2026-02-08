from datetime import datetime, timezone
from sqlite3 import IntegrityError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import UserAlreadyExist
from app.auth.schemas import UserCredentialsSchema, UserSessionSchema
from app.db.models import User, UserSession


class AuthenticationRepository:
    async def create_user(self,
                          session: AsyncSession,
                          email: str,
                          password: bytes):
        try:
            new_user = User(email=email, password=password)
            session.add(new_user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise UserAlreadyExist()
        except Exception:
            await session.rollback()
            raise

    async def read_user_for_email(self,
                                  session: AsyncSession,
                                  email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def read_user_for_id(self,
                                  session: AsyncSession,
                                  user_id: int) -> User | None:
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def read_active_session_by_user_id(self,
                                             session: AsyncSession,
                                             user_id: int) -> UserSession | None:
        stmt = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > datetime.now(timezone.utc),
            )
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user_session(self,
                                  session: AsyncSession,
                                  data: UserSessionSchema):
        try:
            new_user_session = UserSession(user_id=data.user_id,
                                   token_hash=data.token_hash,
                                   expires_at=data.expires_at)
            session.add(new_user_session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


    async def revoke_session(self,
                             session: AsyncSession,
                             user_session: UserSession) -> None:
        if user_session.revoked_at is not None:
            return

        user_session.revoked_at = datetime.now(timezone.utc)
        await session.commit()