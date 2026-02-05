from datetime import datetime, timezone

from sqlalchemy import String, DateTime, LargeBinary
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = 'user_account'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'User(user_id={self.user_id!r}, email={self.email!r}, created_at={self.created_at!r})'