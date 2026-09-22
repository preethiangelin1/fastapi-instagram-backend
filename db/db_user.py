from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from schemas import UserCreate
from db.models import DbUser
from db.hashing import Hash

async def create_user(db: AsyncSession, request: UserCreate):
    result = await db.execute(
        select(DbUser).where(
            func.lower(DbUser.username) == request.username.lower(),
        ),
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = await db.execute(
        select(DbUser).where(func.lower(DbUser.email) == request.email.lower()),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.hash(request.password),
        is_private=request.is_private
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
           select(DbUser).where(
               func.lower(DbUser.username) == username.lower(),
           ),
       )
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with username {username} not found")
    return existing_user

async def get_user_by_id(db: AsyncSession, id: int):
    result = await db.execute(
        select(DbUser).where(
            DbUser.id == id,
        ),
    )
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    return existing_user