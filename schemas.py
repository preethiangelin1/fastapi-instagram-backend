from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    class Config():
        orm_mode = True

class PostBase(BaseModel):
    image_url: str
    image_url_type: str
    caption: str
    user_id: int

# For PostResponse
class User(BaseModel):
    username: str
    class Config():
        orm_mode = True

# For CommentResponse
class Comment(BaseModel):
    text: str
    username: str
    timestamp: datetime
    class Config():
        orm_mode = True

class PostResponse(BaseModel):
    id: int
    image_url: str
    image_url_type: str
    caption: str
    timestamp: datetime
    user: User
    comments: List[Comment]
    class Config():
        orm_mode = True

class UserAuth(BaseModel):
    id: int
    username: str
    email: str

class CommentBase(BaseModel):
    username: str
    text: str
    post_id: int
    