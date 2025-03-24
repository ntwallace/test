import hashlib
import secrets
from typing import Optional

from passlib.context import CryptContext

from app.v1.auth.repositories.api_keys_repository import APIKeysRepository
from app.v1.auth.schemas.api_key import APIKey, APIKeyCreate


DEFAULT_API_KEY_LENGTH = 64


class APIKeysService:

    def __init__(self, api_keys_repository: APIKeysRepository):
        self.api_keys_repository = api_keys_repository
        self.api_key_length = DEFAULT_API_KEY_LENGTH
        self.crypt_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    def _generate_api_key(self) -> str:
        return secrets.token_urlsafe(self.api_key_length)
    
    def _hash_api_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    def _verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest() == hashed_key
    
    def create_api_key(self, name: str) -> tuple[str, APIKey]:
        """
        Generates a new API key and stores it in the database.
        Returns a tuple containing the new API key string and 
        the API key schema from the repository.
        """
        api_key_string = self._generate_api_key()
        hashed_api_key = self._hash_api_key(api_key_string)
        api_key_create = APIKeyCreate(
            name=name,
            api_key_hash=hashed_api_key
        )
        api_key = self.api_keys_repository.create(api_key_create)
        return api_key_string, api_key

    def get_api_key(self, api_key: str) -> Optional[APIKey]:
        api_key_hash = self._hash_api_key(api_key)
        api_keys = self.api_keys_repository.filter_by(api_key_hash=api_key_hash)
        if len(api_keys) == 0:
            return None
        if len(api_keys) > 1:
            raise ValueError("Multiple API keys found with the same hash.")
        return api_keys[0]
