from pathlib import Path
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models import DbPost
from sqlalchemy import select
from schemas import UserAuth
from fastapi import HTTPException, UploadFile, status, Depends
from typing import Annotated
from db.database import get_db
from integrations.s3 import upload_post_image, delete_post_image
import logfire

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
    with logfire.span("post_upload", upload_method="server_proxy", user_id=current_user.id) as span:
        extension = Path(image.filename).suffix.lower()
        filename = f"{uuid4()}{extension}"
        with logfire.span("read image body"):
            file_bytes = await image.read()
        span.set_attribute("file_size_bytes", len(file_bytes))

        with logfire.span("s3_upload"):
            await upload_post_image(file_bytes, filename)

    new_post = DbPost(
        image_file=filename,
        caption=caption,
        user_id=current_user.id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author", "comments", "likes"])

    return new_post

async def get_all(db: AsyncSession):
    result = await db.execute(
            select(DbPost).options(
                selectinload(DbPost.comments),
                selectinload(DbPost.author),
                selectinload(DbPost.likes)
            )
        )
    return result.scalars().all()

async def get_post(id: int, db: AsyncSession):
    result = await db.execute(
            select(DbPost)
                .options(
                    selectinload(DbPost.comments),
                    selectinload(DbPost.author),
                    selectinload(DbPost.likes)
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

    await delete_post_image(existing_post.image_file)

    await db.delete(existing_post)
    await db.commit()

        