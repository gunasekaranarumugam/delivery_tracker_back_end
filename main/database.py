from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()

DB_USER = "admin"
DB_PASSWORD = "Meganathisekaran001"
DB_HOST = "delivery-tracker-data.c38wmw064mzj.ap-south-1.rds.amazonaws.com"
DB_NAME = "delivery_tracker_dev"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def handle_db_error(db: Session, e: Exception, operation: str):
    try:
        db.rollback()
    except Exception:
        pass

    if isinstance(e, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{operation} failed due to a data constraint violation "
                "(e.g., duplicate ID or status name)."
            ),
        )

    if isinstance(e, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"{operation} failed: Database operational error. "
                "Check the SQL syntax or connection."
            ),
        )

    if isinstance(e, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"{operation} failed: A database connection or query "
                "execution error occurred."
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"An unexpected error occurred during the {operation} operation.",
    )
