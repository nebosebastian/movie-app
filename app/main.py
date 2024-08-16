from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import app.models as models, app.schemas as schemas, app.crud as crud
from app.database import get_db, engine, Base
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv

from app.logger import getLogger

#sey up logger
logger = getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration for JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))

# FastAPI app instance
app = FastAPI()

# Create database tables
Base.metadata.create_all(engine)

# Security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    hashed = pwd_context.hash(password)
    print(f"Hashed Password: {hashed}")   
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception

    return user

@app.post("/signup", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["User"])
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info("signing up")
    created_user = crud.create_user(db=db, user=user)
    print(f"Created User: {created_user}") 
    logger.info("user created")
    return created_user



@app.post("/token", response_model=schemas.Token, tags=["User"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info("logining in")
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning("You do not have an account")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    logger.info("Login succesful")
    return {"access_token": access_token, "token_type": "bearer"}


# Movies endpoints
@app.get("/movies/", response_model=List[schemas.Movie], tags=["Movies"])
async def get_movies(skip: int = 0, limit: int = 10,
    db: Session = Depends(get_db)):
    movies = crud.get_movies(db, skip=skip, limit=limit)
    return movies

@app.post("/movie/", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED, tags=["Movies"])
async def create_movie(
    movie: schemas.MoviesCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        return crud.create_movie(db=db, movie=movie, current_user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/movie/{movie_id}", response_model=schemas.Movie, tags=["Movies"])
async def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id=movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

@app.put("/movies/{movie_id}", response_model=schemas.Movie, tags=["Movies"] )
async def update_movie(
    movie_id: int,
    movie_update: schemas.MoviesUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    movie = crud.update_movie(db, movie_id, movie_update, current_user.id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

@app.delete("/movies/{movie_id}", response_model=schemas.Movie, tags=["Movies"])
async def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    movie = crud.delete_movie(db, movie_id, current_user.id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie

# Rating endpoints
@app.post("/ratings/", response_model=schemas.Rating, tags=["Movies"], status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_rating(db, user_id=current_user.id, movie_id=rating.movie_id, rating=rating.rating)

@app.get("/ratings/", tags=["Movies"])
async def read_ratings(user_id: Optional[int] = None, movie_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_ratings(db, user_id=user_id, movie_id=movie_id)

# Comment endpoints
@app.post("/comments/", tags=["Movies"], status_code=201)
async def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_comment(db, user_id=current_user.id, movie_id=comment.movie_id, comment=comment.comment)


@app.get("/comments/", tags=["Movies"])
async def read_comments(user_id: Optional[int] = None, movie_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_comment(db, user_id=user_id, movie_id=movie_id)




@app.post("/comments/reply/", tags=["Movies"])
def create_reply(reply: schemas.ReplyCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return crud.reply_to_comment(db, user_id=current_user.id, comment_id=reply.comment_id, comment=reply.comment)