# main/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base  
import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base 
from urllib.parse import quote

load_dotenv()

# --- SQLAlchemy Base ---


# --- MySQL connection details ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))  # encode special chars
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
