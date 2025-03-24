from datetime import datetime, timezone
from passlib.context import CryptContext

context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return context.verify(password, password_hash)

def convert_to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
