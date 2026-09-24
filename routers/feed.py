from datetime import datetime
from fastapi import APIRouter, Depends
from db import db_feed
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from auth.oauth2 import CurrentUser
from schemas import FeedResponse

router = APIRouter(prefix="/feed", tags=["feed"])

@router.get("/", response_model=FeedResponse)
async def get_feed(
        db: Annotated[AsyncSession, Depends(get_db)],
        current_user: CurrentUser,
        cursor_created_at: datetime | None = None,
        cursor_id: int | None = None,
        limit: int = 20
    ):
    return await db_feed.get_feed(db, current_user, cursor_created_at, cursor_id, limit)