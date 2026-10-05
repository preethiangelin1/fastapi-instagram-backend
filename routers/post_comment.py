from schemas import CommentCreate, UserAuth
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db import db_comment
from auth.oauth2 import get_current_user

router = APIRouter(prefix="/posts", tags=["comment"])

@router.get("/{post_id}/comments")
async def comments(post_id: int, db: AsyncSession = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return await db_comment.get_all(db, post_id)

@router.post("/{post_id}/comments")
async def create(post_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return await db_comment.create(db, current_user, comment, post_id)

@router.patch("/{post_id}/comments/{comment_id}")
async def update(post_id: int, comment_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return await db_comment.update(db, post_id, comment_id, current_user, comment)


@router.delete("/{post_id}/comments/{comment_id}")
async def delete(post_id: int, comment_id: int, db: AsyncSession = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return await db_comment.delete(db, post_id, comment_id, current_user)
