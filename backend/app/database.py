import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

# Vercel injects POSTGRES_URL_NON_POOLING or POSTGRES_URL for standard connections.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or DATABASE_URL.startswith("prisma://"):
    DATABASE_URL = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or DATABASE_URL or "sqlite:///./crm.db"
if DATABASE_URL and DATABASE_URL.startswith("postgres"):
    # Vercel provides postgres:// or postgresql://, SQLAlchemy needs postgresql+pg8000://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]

connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif DATABASE_URL and "pg8000" in DATABASE_URL:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args = {"ssl_context": ctx}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
