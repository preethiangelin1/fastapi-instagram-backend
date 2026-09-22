from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import DbComment, DbFollow
from auth.oauth2 import CurrentUser
from db.db_user import get_user_by_id

async def create(db: AsyncSession, current_user:CurrentUser, user_id:int):

    user = await get_user_by_id(db, user_id)
    status = 'pending' if user.is_private == True else 'accepted'

    new_follow = DbFollow(
        follower_id = current_user.id,
        followee_id = user_id,
        status = status
    )

    db.add(new_follow)
    await db.commit()
    await db.refresh(new_follow)
    return new_follow

async def get_followers(db: AsyncSession, current_user:CurrentUser):
    result = await db.execute(
        select(DbFollow)
            .where(
                and_(
                    DbFollow.followee_id == current_user.id,
                    DbFollow.status == 'accepted'
                )
            )
    )
    return result.scalars().all()

async def update_request(db: AsyncSession, follower_id: int, followee_id: int, status: str):

    await get_user_by_id(db, follower_id)

    result = await db.execute(
        select(DbFollow)
            .where(
                and_(
                    DbFollow.follower_id == follower_id,
                    DbFollow.followee_id == followee_id,
                )
            )
    )
    follow = result.scalars().first()

    if not follow:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Follow request not found")

    follow.status = status
    await db.commit()
    await db.refresh(follow)
    return follow
