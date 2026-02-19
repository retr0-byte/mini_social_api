from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class PostComments(Base):
    __tablename__ = 'post_comments'

    id: Mapped[int] = mapped_column(primary_key=True)

    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    content: Mapped[str] = mapped_column(String(255))

    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc))




    def __repr__(self) -> str:
        return f'PostComment(id={self.id!r}, created_at={self.created_at!r})'