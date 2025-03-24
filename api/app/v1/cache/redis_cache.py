from collections.abc import Mapping
from typing import Optional, Union
from redis import Redis
from app.v1.cache.cache import Cache


class RedisCache(Cache):

    def __init__(
        self,
        redis_host: str,
        redis_port: int,
        database_index: int = 1
    ) -> None:
        self._redis = Redis(
            host=redis_host,
            port=redis_port,
            db=database_index,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=3,
            max_connections=100
        )
    
    def get(self, key: str) -> Optional[str]:
        return self._redis.get(key)
    
    def set(self, key: str, value: Union[str, int, float], expire_in_seconds: Optional[int] = None) -> bool:
        response = self._redis.set(key, value, ex=expire_in_seconds)
        if response is None:
            return False
        return response

    def hget(self, name: str, key: str) -> str | None:
        return self._redis.hget(name, key)

    def hgetall(self, key: str) -> Mapping[str, str | int | float] | None:
        if not self._redis.exists(key):
            return None
        return self._redis.hgetall(key)
