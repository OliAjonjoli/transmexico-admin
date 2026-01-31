"""Database access for admin API - connects to bot's SQLite database."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Use bot's database directly
BOT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../bot/transmexico.db'))
DATABASE_URL = f"sqlite:///{BOT_DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
