from pathlib import Path
from uuid import uuid4
import shutil

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schemas import PostBase
from db.models import DbPost
from sqlalchemy import select
from schemas import UserAuth
from fastapi import HTTPException, UploadFile, status, Depends
from typing import Annotated
from db.database import get_db

MEDIA_POSTS_DIR = Path("media/posts")
MEDIA_POSTS_DIR.mkdir(parents=True, exist_ok=True)


async def create_post(db: AsyncSession, image: UploadFile, caption: str, current_user: UserAuth ):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/avif"
    }

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, AVIF, WebP images are allowed",
        )

    extension = Path(image.filename).suffix.lower()
    filename = f"{uuid4()}{extension}"

    file_path = MEDIA_POSTS_DIR / filename

        # Save image
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)


    new_post = DbPost(
        image_file=filename,
        caption=caption,
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

        