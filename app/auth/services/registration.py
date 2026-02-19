from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.auth.exceptions import UserAlreadyExist
from app.auth.schemas import UserCredentialsSchema
from app.core.base_service import BaseService
from app.repositories import AuthenticationRepository
from app.auth.utils import hash_secret


class RegistrationService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.user_repo = AuthenticationRepository(self.session)

    async def register_user(self, data: UserCredentialsSchema) -> None:
        email: str = data.email # noqa
        password: str = data.password
        hashed_password: bytes = hash_secret(password)

        try:
            await self.user_repo.create_user(
                session=self.session,
                email=email,
                password=hashed_password
            )
        except IntegrityError:
            raise UserAlreadyExist()