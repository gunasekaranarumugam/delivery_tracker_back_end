"""
from sqlalchemy import create_engine
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
        db.close()
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Replace this section for MySQL ---
# Define your database credentials
db_user = "admin"
db_password = "TBs7~T:|k2pXg~cY(JbgW9jsKhYj"
db_host = "delivery-tracker-data.cw3uwuiqequv.us-east-1.rds.amazonaws.com"  # e.g., "localhost" or a server IP
db_name = "delivery_tracker"

# Construct the MySQL database URL
# The format is: "dialect+driver://username:password@host/dbname"
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

# Create the engine, SessionLocal, and Base
# Unlike SQLite, MySQL connections don't require `check_same_thread=False`
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print(get_db)