from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Annotated
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db import db_user
from db.models import DbUser
from config import settings
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
 
SECRET_KEY = settings.secret_key.get_secret_value()
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt
 
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("username")
    if username is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  user = await db_user.get_user_by_username(db, username=username)
  if user is None:
    raise credentials_exception
  return user

CurrentUser = Annotated[DbUser, Depends(get_current_user)]