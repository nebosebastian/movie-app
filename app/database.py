import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Correct the connection string format if needed
# URL_DATABASE = 'mysql+pymysql://root:%4083Ogologo.@localhost:3300/capstone'
URL_DATABASE = os.environ.get('URL_DATABASE')

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
