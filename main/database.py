# main/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base  
import os
from dotenv import load_dotenv

#load_dotenv()

# --- MySQL connection details ---
db_user = "admin"
db_password = "wtjS(fR35oT-<oObw5G#q-L|3c(a"
db_host = "delivery-tracker-db.c38wmw064mzj.ap-south-1.rds.amazonaws.com"  # e.g., "localhost" or a server IP
db_name = "delivery_tracker_dev"

# Construct the database URL
DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

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
