from datetime import UTC, datetime
from config import settings
from db.database import Base
from sqlalchemy import DateTime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class DbUser(Base):

    __tablename__ = "users"
        
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    bio: Mapped[str] = mapped_column(String(300), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    posts: Mapped[list[DbPost]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    following = relationship(
        "DbFollow", foreign_keys="DbFollow.follower_id", back_populates="follower"
    )
    followers = relationship(
        "DbFollow", foreign_keys="DbFollow.followee_id", back_populates="followee"
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
    comments = relationship("DbComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("DbLike", back_populates="post", cascade="all, delete-orphan")

    @property
    def image_path(self) -> str:
        return f"{settings.cloudfront_domain}/{self.image_file}"

class DbFollow(Base):

    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    followee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="accepted", server_default="accepted")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    follower = relationship("DbUser", foreign_keys=[follower_id], back_populates="following")
    followee = relationship("DbUser", foreign_keys=[followee_id], back_populates="followers")

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

class DbLike(Base):

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username"),
        nullable=False,
        index=True,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    post = relationship("DbPost", back_populates="likes")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped[DbUser] = relationship(back_populates="reset_tokens")
    




