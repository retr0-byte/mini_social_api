from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.session import Base


class PostLikes(Base):
    __tablename__ = 'post_likes'

    like_id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.post_id'),
                                                index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.user_id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('post_id', 'user_id'),
    )

    def __repr__(self) -> str:
        return f'PostLike(like_id={self.like_id!r}, created_at={self.created_at!r})'