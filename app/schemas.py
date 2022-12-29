from enum import IntEnum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


# Post schemas
class PostBase(BaseModel):
    title:str
    content: str
    published: bool = False

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author: UserResponse
    created_at: datetime

    class Config:
        orm_mode = True

class PostWithVotes(BaseModel):
    Post: PostResponse
    votes: int

# Auth schemas
class Token(BaseModel):
    token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


# Votes Schemas
class DirEnum(IntEnum):
    like = 1
    dislike = 0


class Vote(BaseModel):
    post_id: int
    dir: DirEnum