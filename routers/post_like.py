from schemas import UserAuth
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db import db_like
from auth.oauth2 import get_current_user

router = APIRouter(prefix="/posts", tags=["like"])

@router.get("/{post_id}/likes")
async def likes(post_id: int, db: AsyncSession = Depends(get_db)):
    return await db_like.get_all(db, post_id)

@router.post("/{post_id}/likes")
async def create(post_id: int, db: AsyncSession = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return await db_like.create(db, current_user, post_id)