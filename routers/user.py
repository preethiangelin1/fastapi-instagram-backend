from schemas import UserBase, UserResponse
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_user
from db.models import DbPost

router = APIRouter(prefix="/users", tags=["user"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, user)