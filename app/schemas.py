from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import date

# User Schemas
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class User(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[str] = None

# Movie Schemas

class MovieBase(BaseModel):
    title: str
    author: str
    release_date: date

class MoviesCreate(MovieBase):
    pass

class MoviesUpdate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    created_by: int

    class Config:
        orm_mode = True

# Rating Schemas

class RatingBase(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: int

class RatingCreate(BaseModel):
    movie_id: int
    rating: int

class Rating(RatingBase):
    model_config = ConfigDict(
        from_attributes=True
    )

# Comment Schemas

class CommentBase(BaseModel):
    id: int
    user_id: int
    movie_id: int
    comment: str

class CommentCreate(BaseModel):
    movie_id: int
    comment: str

class ReplyCreate(BaseModel):
    comment_id: int
    comment: str

class Comment(CommentBase):
    model_config = ConfigDict(
        from_attributes=True
    )
