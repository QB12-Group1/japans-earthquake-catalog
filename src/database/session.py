from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_session():
    """Yields a SQLAlchemy session; use with `with get_session() as session:`."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
