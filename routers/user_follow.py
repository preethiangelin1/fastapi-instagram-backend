from fastapi import APIRouter, status, Depends
from db import db_follow
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from auth.oauth2 import CurrentUser
from schemas import FollowRequestUpdate

router = APIRouter(prefix="/users", tags=["follows"])

@router.post("/{user_id}/follows", status_code=status.HTTP_201_CREATED)
async def create_follow(user_id: int, db: Annotated[AsyncSession, Depends(get_db)],  current_user: CurrentUser,):
    return await db_follow.create(db, current_user, user_id)

@router.get("/me/followers")
async def get_followers(db: Annotated[AsyncSession, Depends(get_db)],  current_user: CurrentUser):
    return await db_follow.get_followers(db, current_user)

@router.patch("/me/follows/{follower_id}")
async def update_follow_request(
    follower_id: int,
    request: FollowRequestUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    return await db_follow.update_request(
        db=db,
        follower_id=follower_id,
        followee_id=current_user.id,
        status=request.status,
    )