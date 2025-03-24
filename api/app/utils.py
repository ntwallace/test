from __future__ import annotations
from collections.abc import Callable
from typing import Optional, TypeVar


_TToMap = TypeVar("_TToMap")
_TMapResult = TypeVar("_TMapResult")


def map_none(
    me: Optional[_TToMap],
    fn: Callable[[_TToMap], _TMapResult],
) -> Optional[_TMapResult]:
    if me is None:
        return me
    return fn(me)


def celsius_to_farenheit_int(c: float) -> int:
    return round(c * 9 / 5 + 32)
