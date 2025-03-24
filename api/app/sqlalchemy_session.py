import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()


POWERX_DATABASE_HOST = os.environ.get('POWERX_DATABASE_HOST', '')
POWERX_DATABASE_PORT = os.environ.get('POWERX_DATABASE_PORT', '')
POWERX_DATABASE_USER = os.environ.get('POWERX_DATABASE_USER', '')
POWERX_DATABASE_PASSWORD = os.environ.get('POWERX_DATABASE_PASSWORD', '')
POWERX_DATABASE_NAME = os.environ.get('POWERX_DATABASE_NAME', '')
POWERX_DATABASE_URL = f"postgresql+psycopg://{POWERX_DATABASE_USER}:{POWERX_DATABASE_PASSWORD}@{POWERX_DATABASE_HOST}:{POWERX_DATABASE_PORT}/{POWERX_DATABASE_NAME}"

engine = create_engine(
    POWERX_DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)