# main/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base  # ✅ Use the same Base from your models
import os
from dotenv import load_dotenv

load_dotenv()

# --- MySQL connection details ---
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

print("DB_USER:", db_user)
print("DB_PASSWORD:", db_password)
print("DB_HOST:", db_host)
print("DB_NAME:", db_name)



# Construct the database URL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
print("Final connection URL:", SQLALCHEMY_DATABASE_URL)

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
