from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base  
import urllib.parse

db_user = "admin"
db_password = "wtjS(fR35oT-<oObw5G#q-L|3c(a"
db_host = "delivery-tracker-db.c38wmw064mzj.ap-south-1.rds.amazonaws.com"
db_name = "delivery_tracker_dev"

encoded_password = urllib.parse.quote_plus(db_password)

DATABASE_URL = f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
