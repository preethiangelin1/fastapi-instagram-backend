from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import DbComment
from schemas import CommentCreate, UserAuth

async def create(db: AsyncSession, current_user:UserAuth, comment: CommentCreate, post_id:int):
    new_comment = DbComment(
        text = comment.text,
        username = current_user.username,
        post_id = post_id,
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    return new_comment

async def get_all(db: AsyncSession, post_id: int):
    result = await db.execute(
        select(DbComment).where(DbComment.post_id == post_id)
    )
    return result.scalars().all()
