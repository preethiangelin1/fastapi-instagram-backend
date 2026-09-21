from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import DbLike
from schemas import UserAuth

async def create(db: AsyncSession, current_user:UserAuth, post_id:int):
    new_like = DbLike(username = current_user.username,  post_id = post_id)

    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)

    return new_like

async def get_all(db: AsyncSession, post_id: int):
    result = await db.execute(
        select(DbLike).where(DbLike.post_id == post_id)
    )
    return result.scalars().all()
