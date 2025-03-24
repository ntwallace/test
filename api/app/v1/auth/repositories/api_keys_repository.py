from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.auth.models.api_key import APIKey as APIKeyModel
from app.v1.auth.schemas.api_key import APIKey, APIKeyCreate


class APIKeysRepository(ABC):

    @abstractmethod
    def create(self, api_key_create: APIKeyCreate) -> APIKey:
        ...
    
    @abstractmethod
    def get(self, api_key_id: UUID) -> Optional[APIKey]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[APIKey]:
        ...
    
    @abstractmethod
    def delete(self, api_key_id: UUID) -> None:
        ...


class PostgresAPIKeysRepository(APIKeysRepository):

    def __init__(self, session: Session):
        self.session = session

    def create(self, api_key_create: APIKeyCreate) -> APIKey:
        try:
            api_key = APIKeyModel(
                name=api_key_create.name,
                api_key_hash=api_key_create.api_key_hash
            )
            self.session.add(api_key)
            self.session.commit()
            self.session.refresh(api_key)
        except IntegrityError:
            raise ValueError('API key with that name already exists')
        return APIKey.model_validate(api_key, from_attributes=True)

    def get(self, api_key_id: UUID) -> Optional[APIKey]:
        api_key = self.session.query(APIKeyModel).filter(APIKeyModel.api_key_id == api_key_id).first()
        if api_key is None:
            return None
        return APIKey.model_validate(api_key, from_attributes=True)
    
    def filter_by(self, **kwargs) -> List[APIKey]:
        api_keys = self.session.query(APIKeyModel).filter_by(**kwargs).all()
        return [
            APIKey.model_validate(api_key, from_attributes=True)
            for api_key in api_keys
        ]

    def delete(self, api_key_id: UUID) -> None:
        api_key = self.session.query(APIKeyModel).filter(APIKeyModel.api_key_id == api_key_id).first()
        if api_key is not None:
            self.session.delete(api_key)
            self.session.commit()
