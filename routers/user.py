from typing import Annotated


from schemas import UserCreate, UserPrivate
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db import db_user
from db.models import DbPost

router = APIRouter(prefix="/users", tags=["user"])

@router.post("/", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await db_user.create_user(db, user)