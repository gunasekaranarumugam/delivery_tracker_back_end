
"""from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite (default)
SQLALCHEMY_DATABASE_URL = "sqlite:///./delivery_tracker.db"
# MySQL example (commented)
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@host/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()"""

# main/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base  # ✅ Use the same Base from your models

# --- MySQL connection details ---
db_user = "admin"
db_password = "TBs7~T:|k2pXg~cY(JbgW9jsKhYj"
db_host = "delivery-tracker-data.cw3uwuiqequv.us-east-1.rds.amazonaws.com"  # e.g., "localhost" or a server IP
db_name = "delivery_tracker"

# Construct the database URL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

# Create SQLAlchemy engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ DO NOT redefine Base here — it comes from models

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
