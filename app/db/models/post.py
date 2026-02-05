from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class Post(Base):
    __tablename__ = 'post'

    post_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user_account.user_id'))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f'Post(post_id={self.post_id!r}, title={self.title!r}, created_at={self.created_at!r})'