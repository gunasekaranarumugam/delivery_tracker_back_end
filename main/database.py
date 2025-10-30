# main/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base  
import os
from dotenv import load_dotenv

load_dotenv()

# --- MySQL connection details ---
db_user = os.environ.get('db_user')
db_password = os.environ.get('db_password')
db_host = os.environ.get('db_host')
db_name = os.environ.get('db_name')

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
