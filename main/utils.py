from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session


def now_utc():
    return datetime.now(timezone.utc)


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
