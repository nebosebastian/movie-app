from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

release_date_str = '2024-08-04'
release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, nullable=False, unique=True, index=True, autoincrement=True)
    username = Column(String(15), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String(500), nullable=False)

    movies = relationship("Movie", back_populates="creator")

class Movie(Base):
    __tablename__ = 'movies'
    
    id = Column(Integer, primary_key=True, nullable=False, unique=True, index=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(50), nullable=False)
    release_date = Column(Date, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    creator = relationship("User", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    comments = relationship("Comment", back_populates="movie")
    
class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, nullable=False, unique=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    
    user = relationship("User")
    movie = relationship("Movie", back_populates="ratings")
    
class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, nullable=False, unique=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    comment = Column(String(500), nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)  
    
    user = relationship("User")
    movie = relationship("Movie", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref='replies')
    