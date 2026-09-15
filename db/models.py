from datetime import UTC, datetime

from db.database import Base
from sqlalchemy import Column, DateTime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DbUser(Base):

    __tablename__ = "users"
        
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    posts: Mapped[list[DbPost]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

class DbPost(Base):

    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_file: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default=None,
    )
    caption: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    author = relationship("DbUser", back_populates="posts")
    comments = relationship(
        "DbComment", 
        back_populates="post",
        cascade="all, delete-orphan")

    @property
    def image_path(self) -> str:
        return f"/media/posts/{self.image_file}"

class DbComment(Base):

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
        index=True,
    )
    post = relationship("DbPost", back_populates="comments")
    




