from __future__ import annotations

from enum import Enum
from typing import Any, Callable, TypeVar

from pydantic import BaseModel


def irange(start: int, stop: int) -> range:
    return range(start, stop + 1)


class StrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[Any]
    ) -> Any:
        return name


class PredicateBackoffDetails(BaseModel):
    target: Callable[..., Any]
    args: list[Any]
    kwargs: dict[str, Any]
    tries: int
    elapsed: float
    value: Any
