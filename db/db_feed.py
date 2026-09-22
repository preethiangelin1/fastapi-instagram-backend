from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models import DbFollow, DbPost, DbUser
from auth.oauth2 import CurrentUser
from sqlalchemy import select, or_, and_, tuple_

from schemas import CursorOut


async def get_feed(
        db: AsyncSession, 
        current_user:CurrentUser,
        cursor_created_at: datetime | None = None,
        cursor_id: int | None = None,
        limit: int = 20,
    ):
    stmt = (
    select(DbPost)
        .join(DbUser, DbUser.id == DbPost.user_id)
        .outerjoin(
            DbFollow,
            and_(
                DbFollow.followee_id == DbPost.user_id,
                DbFollow.follower_id == current_user.id,
            ),
        )
        .options(
            selectinload(DbPost.comments),
            selectinload(DbPost.author),
            selectinload(DbPost.likes)
        )
        .where(
            or_(
                DbPost.user_id == current_user.id,
                DbFollow.status == "accepted",
                DbUser.is_private.is_(False),
            )
        )
        .order_by(DbPost.created_at.desc(), DbPost.id.desc())
        .limit(limit + 1)
    )
    if cursor_created_at is not None and cursor_id is not None:
        stmt = stmt.where(
            tuple_(DbPost.created_at, DbPost.id) < (cursor_created_at, cursor_id)
        )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    has_more = len(posts) > limit
    posts = posts[:limit]

    next_cursor = None
    if has_more and posts:
        last = posts[-1]
        next_cursor = CursorOut(created_at=last.created_at, id=last.id)

    return {
        "posts": posts,
        "next_cursor":next_cursor,
        "has_more": has_more,
    }