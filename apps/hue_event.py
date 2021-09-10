from __future__ import annotations

from datetime import datetime
from enum import auto, unique
from typing import Optional

from pydantic import BaseModel

from util import StrEnum


@unique
class Origin(StrEnum):
    LOCAL = auto()


class Context(BaseModel):
    id: str
    parent_id: Optional[str]
    user_id: Optional[str]


class Metadata(BaseModel):
    origin: Origin
    time_fired: datetime
    context: Context


class Event(BaseModel):
    id: str
    unique_id: str
    event: int
    last_updated: datetime
    metadata: Metadata
