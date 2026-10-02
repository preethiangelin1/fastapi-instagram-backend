from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from analytics import Action, track
from db.models import DbComment
from schemas import CommentCreate, UserAuth
from fastapi import status, HTTPException

async def create(db: AsyncSession, current_user:UserAuth, comment: CommentCreate, post_id:int):
    new_comment = DbComment(
        text = comment.text,
        username = current_user.username,
        post_id = post_id,
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    track(Action.COMMENT_ADDED, user_id=current_user.id, post_id=post_id, comment_id=new_comment.id)

    return new_comment

async def get_all(db: AsyncSession, post_id: int):
    result = await db.execute(
        select(DbComment).where(DbComment.post_id == post_id)
    )
    return result.scalars().all()


async def update(db: AsyncSession, post_id: int, comment_id: int, current_user: UserAuth, comment: CommentCreate):
    result = await db.execute(
            select(DbComment).where(DbComment.post_id == post_id,
                                    DbComment.id == comment_id,
                                    DbComment.username == current_user.username)
        )

    update_comment = result.scalars().first()
    if not update_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id {id} not found")
    
    update_comment.text = comment.text
    await db.commit()
    await db.refresh(update_comment)

    return update_comment


async def delete(db: AsyncSession, post_id: int, comment_id: int, current_user: UserAuth):
    result = await db.execute(
            select(DbComment).where(DbComment.post_id == post_id,
                                    DbComment.id == comment_id,
                                    DbComment.username == current_user.username)
        )

    delete_comment = result.scalars().first()
    if not delete_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment with id {id} not found")

    await db.delete(delete_comment)    
    await db.commit()    
    return "Comment deleted successfully"

