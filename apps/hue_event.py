from __future__ import annotations

from datetime import datetime
from enum import auto, unique
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from util import StrEnum


@unique
class Origin(StrEnum):
    LOCAL = auto()


class Context(BaseModel):
    id: str
    parent_id: Optional[str]
    user_id: Optional[str]


class Event(BaseModel):
    # Human readable switch name, suffixed with "_button"
    id: str
    # Switch's unique ID
    device_id: str
    # Button's unique ID
    unique_id: UUID
    # Event type
    type: str
    # Button number
    subtype: int
