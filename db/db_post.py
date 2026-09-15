from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schemas import PostBase
from db.models import DbPost
from sqlalchemy import select
from schemas import UserAuth
from fastapi import HTTPException, status, Depends
from typing import Annotated
from db.database import get_db


async def create_post(db: AsyncSession, request: PostBase, current_user: UserAuth ):
    new_post = DbPost(
        image_file=request.image_file,
        caption=request.caption,
        user_id=current_user.id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author", "comments"])

    return new_post

async def get_all(db: AsyncSession):
    result = await db.execute(
            select(DbPost).options(
                selectinload(DbPost.comments),
                selectinload(DbPost.author)
            )
        )
    return result.scalars().all()

async def get_post(id: int, db: AsyncSession):
    result = await db.execute(
            select(DbPost)
                .options(
                    selectinload(DbPost.comments),
                    selectinload(DbPost.author)
                )
                .where(
                    DbPost.id == id,
                ),
        )
    existing_post = result.scalars().first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    return existing_post

async def delete_post(id: int, db:  Annotated[AsyncSession, Depends(get_db)], current_user: UserAuth):
    result = await db.execute(
        select(DbPost).where(DbPost.id == id),
    )
    existing_post = result.scalars().first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    await db.delete(existing_post)
    await db.commit()

        