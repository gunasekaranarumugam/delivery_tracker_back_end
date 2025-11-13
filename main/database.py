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
DB_USER = "admin"
DB_PASSWORD = "Meganathisekaran001" # encode special chars
DB_HOST = "delivery-tracker-data.c38wmw064mzj.ap-south-1.rds.amazonaws.com"
DB_NAME = "delivery_tracker_dev"

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
