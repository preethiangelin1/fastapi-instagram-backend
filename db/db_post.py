
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from analytics import Action, track, track_error
from db.models import DbPost
from sqlalchemy import select
from schemas import PostBase, UserAuth
from fastapi import HTTPException, status, Depends
from typing import Annotated
from db.database import get_db
from integrations.s3 import head_object, delete_post_image
from botocore.exceptions import ClientError

async def create_post(post: PostBase, db: AsyncSession, current_user: UserAuth ):
    track(Action.POST_CREATE_ATTEMPTED, user_id=current_user.id)
    try:
        await head_object(post.image_file)
    except ClientError:
        track_error(Action.POST_CREATE_FAILED, user_id=current_user.id, reason="Upload not found in s3")
        raise HTTPException(400, "Upload not found")

    new_post = DbPost(
        image_file=post.image_file,
        caption=post.caption,
        user_id=current_user.id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author", "comments", "likes"])

    track(Action.POST_CREATED, user_id=current_user.id, post_id=new_post.id)

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



        