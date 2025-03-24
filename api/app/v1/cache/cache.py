from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Optional, Union


class Cache(ABC):

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set(self, key: str, value: Union[str, int, float], expire_in_seconds: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    def hget(self, name: str, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def hgetall(self, key: str) -> Mapping[str, str | int | float] | None:
        pass
