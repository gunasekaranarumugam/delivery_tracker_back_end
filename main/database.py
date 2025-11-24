from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

DB_USER = "admin"
DB_PASSWORD = "Meganathisekaran001"
DB_HOST = "delivery-tracker-data.c38wmw064mzj.ap-south-1.rds.amazonaws.com"
DB_NAME = "delivery_tracker"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
