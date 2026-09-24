from typing import List
from fastapi import APIRouter, status, Depends, UploadFile,File
from schemas import PostBase, PostResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db import db_post
import random
import string
import shutil
from schemas import UserAuth
from auth.oauth2 import get_current_user

router = APIRouter(prefix="/posts", tags=["post"])

@router.post("/", response_model=PostResponse)
async def create_post(
        post: PostBase,
        db: AsyncSession = Depends(get_db), 
        current_user: UserAuth = Depends(get_current_user)):
    
    return await db_post.create_post(post, db, current_user)

@router.get("/", response_model=List[PostResponse])
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    return await db_post.get_all(db)

@router.get('/{id}', response_model=PostResponse)
async def get_post(id: int, db: AsyncSession = Depends(get_db)):
    return await db_post.get_post(id, db)

@router.post("/image-upload")
async def upload_image(image: UploadFile = File(...), current_user: UserAuth = Depends(get_current_user)):
    letters = string.ascii_letters
    rand_str = "".join(random.choice(letters) for i in range(6))
    new = f"_{rand_str}."
    filename = new.join(image.filename.rsplit(".", 1))
    path = f"media/posts/{filename}"

    with open(path, "w+b") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return {"filename": path}


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: AsyncSession = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    return await db_post.delete_post(id, db, current_user)

