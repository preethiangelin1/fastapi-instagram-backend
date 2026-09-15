from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from db.hashing import Hash
from auth.oauth2 import create_access_token
from db.models import DbUser


router = APIRouter(tags=["authentication"])

@router.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DbUser).where(
            func.lower(DbUser.username) == request.username.lower(),
        ),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username or password")
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username or password")

    access_token = create_access_token(data={"username": user.username})

    return{
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }




