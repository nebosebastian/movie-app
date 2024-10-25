from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import app.models as models
import app.schemas as schemas   
from passlib.context import CryptContext
from typing import Optional


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
 

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()




# Movie CRUD operations
def delete_movie(db: Session, movie_id: int, user_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id, models.Movie.created_by == user_id).first()
    if movie:
        db.delete(movie)
        db.commit()
        return movie
    return None

def update_movie(db: Session, movie_id: int, movie_update: schemas.MoviesUpdate, current_user: models.User):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        return None
    for key, value in movie_update.dict(exclude_unset=True).items():
        setattr(movie, key, value)
    db.commit()
    db.refresh(movie)
    return movie

def get_movies(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Movie).offset(skip).limit(limit).all()


def create_movie(db: Session, movie: schemas.MoviesCreate, current_user_id: int):
    db_movie = models.Movie(
        title=movie.title,
        author=movie.author,
        release_date=movie.release_date,
        created_by=current_user_id  # Automatically set by the logged-in user
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie
def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()










# Rating CRUD operations
def create_rating(db: Session, user_id: int, movie_id: int, rating: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    new_rating = models.Rating(user_id=user_id, movie_id=movie_id, rating=rating)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

def get_ratings(db: Session, user_id: Optional[int] = None, movie_id: Optional[int] = None):
    query = db.query(models.Rating)
    
    if user_id is not None:
        query = query.filter(models.Rating.user_id == user_id)
        
    if movie_id is not None:
        query = query.filter(models.Rating.movie_id == movie_id)
        
    return query.all()


# Comment CRUD operations
def create_comment(db: Session, user_id: int, movie_id: int, comment: str, parent_id: Optional[int] = None):
    db_comment = models.Comment(user_id=user_id, movie_id=movie_id, comment=comment, parent_id=parent_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    print(f"Created comment: {db_comment}")  # Debug log
    return db_comment

def get_comment(db: Session, user_id: Optional[int] = None, movie_id: Optional[int] = None):
    query = db.query(models.Comment)
    if user_id is not None:
        query = query.filter(models.Comment.user_id == user_id)
    if movie_id is not None:
        query = query.filter(models.Comment.movie_id == movie_id)
    return query.all()




def reply_to_comment(db: Session, user_id: int, comment_id: int, comment: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    parent_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not parent_comment:
        raise HTTPException(status_code=404, detail=f"Comment with ID {comment_id} not found")

    new_comment = models.Comment(
        user_id=user_id,
        movie_id=parent_comment.movie_id,
        comment=comment,
        parent_id=parent_comment.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment