from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile,File
from schemas import PostBase, PostResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_post
from db.models import DbPost
import random
import string
import shutil
from schemas import UserAuth
from auth.oauth2 import get_current_user

router = APIRouter(prefix="/posts", tags=["post"])

image_url_types = ["absolute", "relative"]

@router.post("/", response_model=PostResponse)
def create_post(post: PostBase, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    if not post.image_url_type in image_url_types:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Parameter imagae_url_type can only take values absolute and relative")
    return db_post.create_post(db, post)

@router.get("/", response_model=List[PostResponse])
def get_all_posts(db: Session = Depends(get_db)):
    return db.query(DbPost).all()

@router.get('/{id}')
def get_post(id: int, db: Session = Depends(get_db)):
    db_post = db.query(DbPost).filter(DbPost.id == id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return db_post

@router.post("/image")
def upload_image(image: UploadFile = File(...), current_user: UserAuth = Depends(get_current_user)):
    letters = string.ascii_letters
    rand_str = "".join(random.choice(letters) for i in range(6))
    new = f"_{rand_str}."
    filename = new.join(image.filename.rsplit(".", 1))
    path = f"images/{filename}"

    with open(path, "w+b") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return {"filename": path}


@router.delete('/{id}')
def delete_post(id: int, db: Session = Depends(get_db), current_user: UserAuth = Depends(get_current_user)):
    db_post = db.query(DbPost).filter(DbPost.id == id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Only post creator can delete a post")
    

    db.delete(db_post)    
    db.commit()    
    return "Post deleted successfully"

